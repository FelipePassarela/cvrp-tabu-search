from .busca import (
    ParametrosBusca,
    ProgressoBusca,
    avaliar_inversoes,
    movimento_bloqueado,
    registrar_movimento_tabu,
)
from .experimento import executar_experimento
from .instancias import carregar_instancia_padrao
from .rotas import (
    fit,
)


def melhor_vizinho(frota, custo_total, coordenadas, deposito, lista_tabu, iteracao, melhor_custo):
    movimento = None
    menor_custo = None

    for id_veiculo, veiculo in enumerate(frota):
        rota = veiculo.rota

        if len(rota) < 2:
            continue

        custo_sem_rota = custo_total - fit(rota, coordenadas, deposito)
        inversoes = avaliar_inversoes(rota, coordenadas, deposito, custo_sem_rota)

        for inicio, fim, nova_rota, custo, chave in inversoes:
            if movimento_bloqueado(lista_tabu, chave, iteracao, custo, melhor_custo):
                continue

            if menor_custo is None or custo < menor_custo:
                menor_custo = custo
                movimento = (id_veiculo, inicio, fim, nova_rota, custo, chave)

    return movimento


def busca_tabu(frota, coordenadas, deposito, tau, iteracoes, parada, inicio_execucao):
    progresso = ProgressoBusca(frota, coordenadas, deposito, inicio_execucao)
    custo_atual = progresso.melhor_custo
    lista_tabu = {}

    for iteracao in range(1, iteracoes + 1):
        movimento = melhor_vizinho(
            frota, custo_atual, coordenadas, deposito, lista_tabu,
            iteracao, progresso.melhor_custo,
        )

        if movimento is None:
            break

        id_veiculo, _, _, nova_rota, custo_atual, chave = movimento
        frota[id_veiculo].rota = nova_rota

        registrar_movimento_tabu(lista_tabu, (chave,), iteracao, tau)
        progresso.registrar_iteracao(iteracao, frota, custo_atual)
        if progresso.iteracoes_sem_melhora >= parada:
            break

    return progresso.resultado()


def main():
    instancia = carregar_instancia_padrao()
    parametros = ParametrosBusca(iteracoes=10, parada=10)
    executar_experimento(instancia, busca_tabu, parametros)


if __name__ == "__main__":
    main()
