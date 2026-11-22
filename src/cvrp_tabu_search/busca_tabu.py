import csv
import random
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt

class Veiculo:
    def __init__(self, capacidade):
        self.capacidade = capacidade
        self.carga = 0
        self.rota = []

    def aumentar_carga(self, carga_rota):
        self.carga += carga_rota

    def aumentar_rota(self, cliente):
        self.rota.append(cliente)

    def adicionar_cliente(self, cliente, demanda):
        if (self.carga + demanda) > self.capacidade:
            return False
        
        self.aumentar_carga(demanda)
        self.aumentar_rota(cliente)

        return True

def distancia(cliente_a, cliente_b, coordenadas):
    # Pegando as coordenadas, tem que usar o -1 porque a lista insere na posicao 0 pra frente quando pega do .vrp
    x_a, y_a = coordenadas[cliente_a - 1]
    x_b, y_b = coordenadas[cliente_b - 1]

    aux_x = (x_b - x_a) ** 2
    aux_y = (y_b - y_a) ** 2

    # So calculando a distancia euclidiana mesmo
    euclid = int(((aux_x + aux_y ) ** 0.5) + 0.5)

    return euclid

def fit(rota, coordenadas, deposito):
    custo = 0
    anterior = deposito

    for cliente in rota:
        custo += distancia(anterior, cliente, coordenadas)
        anterior = cliente

    custo += distancia(anterior, deposito, coordenadas)

    return custo

def solucao_inicial(veiculos, dimensao, capacidade, demandas, deposito):
    frota = []
    clientes = []

    for _ in range(veiculos):
        frota.append(Veiculo(capacidade))

    for cliente in range(1, dimensao + 1):
        if cliente != deposito:
            clientes.append(cliente)

    # Aqui é pra usar dentro da .sort e conseguir ordenar os clientes por demandas
    def demanda_cliente(cliente):
        return demandas[cliente - 1]
    
    clientes.sort(key = demanda_cliente, reverse = True)

    for cliente in clientes:
        demanda = demanda_cliente(cliente)
        alocado = False

        for veiculo in frota:
            if veiculo.adicionar_cliente(cliente, demanda):
                alocado = True
                break

        if not alocado:
            return None

    return frota

# Gerar uma possivel rota
def inverter(rota, inicio, fim):
    nova_rota = rota.copy()
    
    trecho = nova_rota[inicio:fim + 1]
    trecho.reverse()

    nova_rota[inicio:fim + 1] = trecho

    return nova_rota

def considerar_movimento(melhor_movimento, novas_rotas, novo_custo, chaves_teste,
                         chaves_tabu, clientes_movidos, lista_tabu, iteracao,
                         melhor_custo, frequencia, diversificar):
    for chave in chaves_teste:
        bloqueio = lista_tabu.get(chave, 0)
        if iteracao <= bloqueio and novo_custo >= melhor_custo:
            return melhor_movimento

    prioridade = (novo_custo,)
    if diversificar:
        vezes_movidos = 0
        for cliente in clientes_movidos:
            vezes_movidos += frequencia.get(cliente, 0)
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
    custos_rotas = []

    for veiculo in frota:
        custos_rotas.append(fit(veiculo.rota, coordenadas, deposito))

    for id_a, veiculo_a in enumerate(frota):
        rota_a = veiculo_a.rota

        if not diversificar:
            for inicio in range(len(rota_a) - 1):
                for fim in range(inicio + 1, len(rota_a)):
                    nova_rota = inverter(rota_a, inicio, fim)
                    novo_custo = custo_atual - custos_rotas[id_a]
                    novo_custo += fit(nova_rota, coordenadas, deposito)

                    primeiro, ultimo = rota_a[inicio], rota_a[fim]
                    chave = ("inverter", min(primeiro, ultimo), max(primeiro, ultimo))
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


def copiar_rotas(frota):
    rotas = []
    for veiculo in frota:
        rotas.append(veiculo.rota.copy())
    return rotas


def busca_tabu(frota, coordenadas, deposito, tau, iteracoes, parada, inicio_execucao,
               demandas, usar_fases=True):
    custo_atual, piora = 0, 0
    lista_tabu = {}
    frequencia = {}
    passos_intensificacao = 0

    for veiculo in frota:
        custo_atual += fit(veiculo.rota, coordenadas, deposito)

    melhor_custo = custo_atual
    melhores_rotas = copiar_rotas(frota)
    historico = [(0, melhor_custo, perf_counter() - inicio_execucao, custo_atual)]

    for iteracao in range(1, iteracoes + 1):
        diversificar = False

        if usar_fases:
            if piora == 10:
                for id_veiculo, veiculo in enumerate(frota):
                    veiculo.rota = melhores_rotas[id_veiculo].copy()
                    veiculo.carga = 0
                    for cliente in veiculo.rota:
                        veiculo.carga += demandas[cliente - 1]
                custo_atual = melhor_custo
                passos_intensificacao = 3

            if piora > 0 and piora % 20 == 0:
                diversificar = True

        intensificar = passos_intensificacao > 0
        movimento = melhor_vizinho(
            frota, custo_atual, coordenadas, deposito, demandas, lista_tabu,
            iteracao, melhor_custo, frequencia, intensificar, diversificar
        )

        if movimento is None and (intensificar or diversificar):
            passos_intensificacao = 0
            movimento = melhor_vizinho(
                frota, custo_atual, coordenadas, deposito, demandas, lista_tabu,
                iteracao, melhor_custo, frequencia
            )

        if movimento is None:
            break

        for id_veiculo, nova_rota, nova_carga in movimento["rotas"]:
            frota[id_veiculo].rota = nova_rota
            frota[id_veiculo].carga = nova_carga
        custo_atual = movimento["custo"]

        if custo_atual < melhor_custo:
            melhor_custo = custo_atual
            melhores_rotas = copiar_rotas(frota)
            piora = 0
        else:
            piora += 1

        duracao_tabu = random.randint(*tau)
        for chave in movimento["chaves_tabu"]:
            lista_tabu[chave] = iteracao + duracao_tabu

        for cliente in movimento["clientes"]:
            frequencia[cliente] = frequencia.get(cliente, 0) + 1

        if passos_intensificacao > 0:
            passos_intensificacao -= 1

        tempo_s = perf_counter() - inicio_execucao
        historico.append((iteracao, melhor_custo, tempo_s, custo_atual))

        if piora >= parada:
            break

    return melhores_rotas, melhor_custo, historico


def leitura(arquivo):
    secao = ""
    veiculos, dimensao, capacidade, deposito = 0, 0, 0, 0
    coordenadas, demandas = [], []

    with open(arquivo, "r", encoding = "utf-8") as arquivo:
        for linha in arquivo:
            if 'EOF' in linha:
                break
            if ":" in linha:
                campo, valor = linha.split(":", 1)
                campo = campo.strip()
                valor = valor.strip()

                if campo == "NAME":
                    veiculos = valor.split("-")[-1]
                    veiculos = int(veiculos.split("k")[-1])
                elif campo == "DIMENSION":
                    dimensao = int(valor)
                elif campo == "CAPACITY":
                    capacidade = int(valor)

            lista_aux = linha.split()
            if "NODE_COORD_SECTION" in linha:
                secao = "NODE_COORD_SECTION"
            elif "DEMAND_SECTION" in linha:
                secao = "DEMAND_SECTION"
            elif "DEPOT_SECTION" in linha:
                secao = "DEPOT_SECTION"
            elif secao == "NODE_COORD_SECTION":
                posi1, posi2 = lista_aux[1:]
                coordenadas.append([float(posi1), float(posi2)])
            elif secao == "DEMAND_SECTION":
                demanda = lista_aux[1]
                demandas.append(int(demanda))
            elif secao == "DEPOT_SECTION":
                if "-1" in lista_aux:
                    secao = ""
                    continue
                deposito = int(lista_aux[0])

    return veiculos, dimensao, capacidade, coordenadas, demandas, deposito

def salvar_csv(caminho, cabecalho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)

def gerar_graficos(instancia, otimo, melhor_historico, medicoes_ttt):
    plt.style.use("default")

    iteracoes = []
    custos = []

    for iteracao, _, _, custo_atual in melhor_historico[1:]:
        iteracoes.append(iteracao)
        custos.append(custo_atual)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(iteracoes, custos, color="tab:blue", label="Custo da iteração")
    ax.axhline(otimo, color="tab:orange", linestyle="--", label=f"Ótimo: {otimo}")
    ax.set_title(f"Evolução da busca tabu — {instancia}")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Custo total")
    ax.legend()

    fig.tight_layout()
    fig.savefig(f"evolucao_tabu_{instancia}.png", dpi=200)
    plt.close(fig)

    tempos_alvo = []
    maior_tempo_total = 0

    for tempo_total, tempo_alvo in medicoes_ttt:
        maior_tempo_total = max(maior_tempo_total, tempo_total)
        if tempo_alvo is not None:
            tempos_alvo.append(tempo_alvo)

    tempos_alvo.sort()
    total_execucoes = len(medicoes_ttt)
    tempos = [0]
    porcentagens = [0]

    for acertos, tempo in enumerate(tempos_alvo, start=1):
        tempos.append(tempo)
        porcentagens.append(100 * acertos / total_execucoes)

    tempos.append(maior_tempo_total)
    porcentagens.append(porcentagens[-1])

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.step(
        tempos, porcentagens, where="post", color="tab:blue",
        label=f"Alvo {otimo}: {len(tempos_alvo)} de {total_execucoes}"
    )
    ax.set_title(f"Time-to-Target — {instancia}")
    ax.set_xlabel("Tempo decorrido (s)")
    ax.set_ylabel("Execuções que atingiram o alvo (%)")
    ax.set_ylim(-4, 104)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.legend()

    fig.tight_layout()
    fig.savefig(f"ttt_tabu_{instancia}.png", dpi=200)
    plt.close(fig)

def main():
    instancia = "A-n32-k5"
    otimo, iteracoes, parada = 784, 60, 30
    tau = (3, 7)

    resultados, melhor_historico, medicoes_ttt = [], [], []
    menor_custo = None

    arquivo = Path(__file__).with_name("data") / f"{instancia}.vrp"
    veiculos, dimensao, capacidade, coordenadas, demandas, deposito = leitura(arquivo)

    for repeticao in range(1, 6):
        semente = repeticao
        random.seed(semente)

        inicio_execucao = perf_counter()
        frota = solucao_inicial(veiculos, dimensao, capacidade, demandas, deposito)

        if frota is None:
            print("Impossivel montar a solucao inicial, deu algum b.o aqui")
            return
        
        _, custo, historico = busca_tabu(
            frota, coordenadas, deposito, tau, iteracoes, parada, inicio_execucao, demandas
        )
        tempo_total_s = perf_counter() - inicio_execucao

        tempo_melhor_s = None
        tempo_alvo_s = None
        for _, custo_na_iteracao, tempo_s, _ in historico:
            if tempo_melhor_s is None and custo_na_iteracao == custo:
                tempo_melhor_s = tempo_s
            if tempo_alvo_s is None and custo_na_iteracao <= otimo:
                tempo_alvo_s = tempo_s

        resultados.append([
            instancia, repeticao, semente, tau[0], tau[1], iteracoes, parada,
            otimo, custo, tempo_melhor_s, tempo_total_s, tempo_alvo_s
        ])

        medicoes_ttt.append((tempo_total_s, tempo_alvo_s))

        if menor_custo is None or custo < menor_custo:
            menor_custo = custo
            melhor_historico = historico

        print(f"Execução {repeticao}: custo {custo} | tempo {tempo_total_s:.3f} s")

    salvar_csv(
        f"execucoes_tabu_{instancia}.csv",
        ["instancia", "repeticao", "semente", "tau_min", "tau_max",
         "limite_iteracoes", "limite_sem_melhora", "otimo", "melhor_custo",
         "tempo_melhor_s", "tempo_total_s", "tempo_alvo_s"],
        resultados
    )

    salvar_csv(
        f"historico_tabu_{instancia}.csv",
        ["iteracao", "melhor_custo", "tempo_s", "custo_atual"],
        melhor_historico[1:]
    )

    gerar_graficos(instancia, otimo, melhor_historico, medicoes_ttt)

    return 

if __name__ == "__main__":
    main()
