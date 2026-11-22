from functools import partial

from .busca import (
    ParametrosBusca,
    ProgressoBusca,
    avaliar_inversoes,
    movimento_bloqueado,
    registrar_movimento_tabu,
)
from .experimento import executar_experimento
from .instancias import carregar_instancia_padrao
from .relatorios import gerar_graficos as _gerar_graficos
from .rotas import (
    fit,
)

PREFIXO_RELATORIOS = "tabu_"


def considerar_movimento(melhor_movimento, novas_rotas, novo_custo, chaves_teste,
                         chaves_tabu, clientes_movidos, lista_tabu, iteracao,
                         melhor_custo, frequencia, diversificar):
    for chave in chaves_teste:
        if movimento_bloqueado(lista_tabu, chave, iteracao, novo_custo, melhor_custo):
            return melhor_movimento

    prioridade = (novo_custo,)
    if diversificar:
        vezes_movidos = sum(frequencia.get(cliente, 0) for cliente in clientes_movidos)
        prioridade = (vezes_movidos, novo_custo)

    if melhor_movimento is None or prioridade < melhor_movimento["prioridade"]:
        return {
            "rotas": novas_rotas,
            "custo": novo_custo,
            "chaves_tabu": chaves_tabu,
            "clientes": clientes_movidos,
            "prioridade": prioridade
        }

    return melhor_movimento


def melhor_vizinho(frota, custo_atual, coordenadas, deposito, demandas,
                   lista_tabu, iteracao, melhor_custo, frequencia,
                   intensificar=False, diversificar=False):
    movimento = None
    custos_rotas = [fit(veiculo.rota, coordenadas, deposito) for veiculo in frota]

    for id_a, veiculo_a in enumerate(frota):
        rota_a = veiculo_a.rota

        if not diversificar:
            custo_sem_rota = custo_atual - custos_rotas[id_a]
            inversoes = avaliar_inversoes(rota_a, coordenadas, deposito, custo_sem_rota)
            for _, _, nova_rota, novo_custo, extremos in inversoes:
                chave = ("inverter", *extremos)
                novas_rotas = [(id_a, nova_rota, veiculo_a.carga)]
                movimento = considerar_movimento(
                    movimento, novas_rotas, novo_custo, (chave,), (chave,),
                    (), lista_tabu, iteracao, melhor_custo, frequencia, False
                )

        # Na intensificacao, conserva a distribuicao da melhor solucao.
        if intensificar:
            continue

        for id_b, veiculo_b in enumerate(frota):
            if id_a == id_b:
                continue

            rota_b = veiculo_b.rota
            custo_sem_rotas = custo_atual - custos_rotas[id_a] - custos_rotas[id_b]

            for posicao_a, cliente_a in enumerate(rota_a):
                demanda_a = demandas[cliente_a - 1]

                # Reinsercao em outra rota, mantendo as K rotas usadas.
                carga_b = veiculo_b.carga + demanda_a
                if len(rota_a) > 1 and carga_b <= veiculo_b.capacidade:
                    nova_rota_a = rota_a.copy()
                    nova_rota_a.pop(posicao_a)
                    custo_sem_cliente = custo_sem_rotas + fit(nova_rota_a, coordenadas, deposito)
                    carga_a = veiculo_a.carga - demanda_a

                    for posicao_b in range(len(rota_b) + 1):
                        nova_rota_b = rota_b.copy()
                        nova_rota_b.insert(posicao_b, cliente_a)
                        novo_custo = custo_sem_cliente + fit(nova_rota_b, coordenadas, deposito)
                        novas_rotas = [(id_a, nova_rota_a, carga_a), (id_b, nova_rota_b, carga_b)]
                        movimento = considerar_movimento(
                            movimento, novas_rotas, novo_custo,
                            (("voltar", cliente_a, id_b),), (("voltar", cliente_a, id_a),),
                            (cliente_a,), lista_tabu, iteracao, melhor_custo,
                            frequencia, diversificar
                        )

                # Cada par de veiculos precisa ser testado uma vez para a troca.
                if id_b < id_a:
                    continue

                for posicao_b, cliente_b in enumerate(rota_b):
                    demanda_b = demandas[cliente_b - 1]
                    carga_a = veiculo_a.carga - demanda_a + demanda_b
                    carga_b = veiculo_b.carga - demanda_b + demanda_a
                    if carga_a > veiculo_a.capacidade or carga_b > veiculo_b.capacidade:
                        continue

                    nova_rota_a = rota_a.copy()
                    nova_rota_b = rota_b.copy()
                    nova_rota_a[posicao_a] = cliente_b
                    nova_rota_b[posicao_b] = cliente_a
                    novo_custo = custo_sem_rotas + fit(nova_rota_a, coordenadas, deposito)
                    novo_custo += fit(nova_rota_b, coordenadas, deposito)
                    novas_rotas = [(id_a, nova_rota_a, carga_a), (id_b, nova_rota_b, carga_b)]

                    chaves_teste = (("voltar", cliente_a, id_b), ("voltar", cliente_b, id_a))
                    chaves_tabu = (("voltar", cliente_a, id_a), ("voltar", cliente_b, id_b))
                    movimento = considerar_movimento(
                        movimento, novas_rotas, novo_custo, chaves_teste, chaves_tabu,
                        (cliente_a, cliente_b), lista_tabu, iteracao, melhor_custo,
                        frequencia, diversificar
                    )

    return movimento


def busca_tabu(frota, coordenadas, deposito, tau, iteracoes, parada, inicio_execucao,
               demandas, usar_fases=True):
    progresso = ProgressoBusca(frota, coordenadas, deposito, inicio_execucao)
    custo_atual = progresso.melhor_custo
    lista_tabu = {}
    frequencia = {}
    passos_intensificacao = 0

    for iteracao in range(1, iteracoes + 1):
        iteracoes_sem_melhora = progresso.iteracoes_sem_melhora

        if usar_fases and iteracoes_sem_melhora == 10:
            _restaurar_rotas(frota, progresso.melhores_rotas, demandas)
            custo_atual = progresso.melhor_custo
            passos_intensificacao = 3

        intensificar = passos_intensificacao > 0
        diversificar = (
                usar_fases
                and iteracoes_sem_melhora > 0
                and iteracoes_sem_melhora % 20 == 0
        )
        movimento = melhor_vizinho(
            frota, custo_atual, coordenadas, deposito, demandas, lista_tabu,
            iteracao, progresso.melhor_custo, frequencia, intensificar, diversificar
        )

        if movimento is None and (intensificar or diversificar):
            passos_intensificacao = 0
            movimento = melhor_vizinho(
                frota, custo_atual, coordenadas, deposito, demandas, lista_tabu,
                iteracao, progresso.melhor_custo, frequencia
            )

        if movimento is None:
            break

        for id_veiculo, nova_rota, nova_carga in movimento["rotas"]:
            frota[id_veiculo].rota = nova_rota
            frota[id_veiculo].carga = nova_carga
        custo_atual = movimento["custo"]

        registrar_movimento_tabu(lista_tabu, movimento["chaves_tabu"], iteracao, tau)

        for cliente in movimento["clientes"]:
            frequencia[cliente] = frequencia.get(cliente, 0) + 1

        if passos_intensificacao > 0:
            passos_intensificacao -= 1

        progresso.registrar_iteracao(iteracao, frota, custo_atual)
        if progresso.iteracoes_sem_melhora >= parada:
            break

    return progresso.resultado()


def _restaurar_rotas(frota, rotas, demandas):
    for veiculo, rota in zip(frota, rotas, strict=True):
        veiculo.rota = rota.copy()
        veiculo.carga = sum(demandas[cliente - 1] for cliente in rota)


def gerar_graficos(instancia, otimo, melhor_historico, medicoes_ttt):
    _gerar_graficos(
        instancia, otimo, melhor_historico, medicoes_ttt, prefixo=PREFIXO_RELATORIOS
    )


def main():
    instancia = carregar_instancia_padrao()
    parametros = ParametrosBusca(iteracoes=60, parada=30)
    busca = partial(busca_tabu, demandas=instancia.demandas)
    executar_experimento(instancia, busca, parametros, prefixo=PREFIXO_RELATORIOS)


if __name__ == "__main__":
    main()
