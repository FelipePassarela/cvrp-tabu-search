import random
import csv
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

def melhor_vizinho(frota, custo_total, coordenadas, deposito, lista_tabu, iteracao, melhor_custo):
    movimento, custo = None, None
    
    for id_veiculo, veiculo in enumerate(frota):
        rota = veiculo.rota

        if len(rota) < 2:
            continue

        custo_original = fit(rota, coordenadas, deposito)

        for inicio in range(len(rota) - 1):

            for fim in range(inicio + 1, len(rota)):               
                nova_rota = inverter(rota, inicio, fim)
                custo_nova_rota = fit(nova_rota, coordenadas, deposito)
                possivel_custo = custo_total - custo_original + custo_nova_rota
                
                # Pra conseguir fazer o bloqueio na busca
                chave = (min(rota[inicio], rota[fim]), max(rota[inicio], rota[fim]))
                bloqueio = lista_tabu.get(chave, 0)

                if iteracao <= bloqueio and possivel_custo >= melhor_custo:
                    continue

                if custo is None or possivel_custo < custo:
                    custo = possivel_custo
                    movimento = (id_veiculo, inicio, fim, nova_rota, custo, chave)

    return movimento

def busca_tabu(frota, coordenadas, deposito, tau, iteracoes, parada, inicio_execucao):
    custo_atual, piora = 0, 0
    melhores_rotas = []
    lista_tabu = {}

    for veiculo in frota:
        custo_atual += fit(veiculo.rota, coordenadas, deposito)
        melhores_rotas.append(veiculo.rota.copy())

    melhor_custo = custo_atual
    historico = [(0, melhor_custo, perf_counter() - inicio_execucao, custo_atual)]

    for iteracao in range(1, iteracoes + 1):
        movimento = melhor_vizinho(frota, custo_atual, coordenadas, deposito, lista_tabu, iteracao, melhor_custo)

        if movimento is None:
            break

        id_veiculo, _, _, nova_rota, novo_custo, chave = movimento
        frota[id_veiculo].rota = nova_rota
        custo_atual = novo_custo

        duracao_tabu = random.randint(*tau)
        lista_tabu[chave] = iteracao + duracao_tabu

        if custo_atual < melhor_custo:
            melhor_custo = custo_atual
            melhores_rotas = []

            for veiculo in frota:
                melhores_rotas.append(veiculo.rota.copy())

            piora = 0
        else:
            piora += 1

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

    # A posição 0 do histórico é a solução inicial.
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
    fig.savefig(f"evolucao_{instancia}.png", dpi=200)
    plt.close(fig)

    tempos_alvo = []
    maior_tempo_total = 0

    for tempo_total, tempo_alvo in medicoes_ttt:
        maior_tempo_total = max(maior_tempo_total, tempo_total)
        if tempo_alvo is not None:
            tempos_alvo.append(tempo_alvo)

    tempos_alvo.sort()
    total = len(medicoes_ttt)
    tempos = [0]
    porcentagens = [0]

    for acertos, tempo in enumerate(tempos_alvo, start=1):
        tempos.append(tempo)
        porcentagens.append(100 * acertos / total)

    # Estende a curva até o fim do tempo observado.
    tempos.append(maior_tempo_total)
    porcentagens.append(porcentagens[-1])

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.step(
        tempos, porcentagens, where="post", color="tab:blue",
        label=f"Alvo {otimo}: {len(tempos_alvo)} de {total}"
    )

    ax.set_title(f"Time-to-Target — {instancia}")
    ax.set_xlabel("Tempo decorrido (s)")
    ax.set_ylabel("Execuções que atingiram o alvo (%)")
    ax.set_ylim(-4, 104)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.legend()

    fig.tight_layout()
    fig.savefig(f"ttt_{instancia}.png", dpi=200)
    plt.close(fig)

def main():
    instancia = "A-n32-k5"
    otimo, iteracoes, parada = 784, 10, 10
    tau = (3, 7)

    resultados, melhor_historico, medicoes_ttt = [], [], []
    menor_custo = None

    arquivo = f"Instancias_melhoria/{instancia}.vrp"
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
            frota, coordenadas, deposito, tau, iteracoes, parada, inicio_execucao
        )
        tempo_total_s = perf_counter() - inicio_execucao

        tempo_melhor_s = None
        tempo_alvo_s = None
        for _, custo_na_iteracao, tempo_s, _ in historico:
            if tempo_melhor_s is None and custo_na_iteracao == custo:
                tempo_melhor_s = tempo_s
            if tempo_alvo_s is None and custo_na_iteracao <= otimo:
                tempo_alvo_s = tempo_s

        medicoes_ttt.append((tempo_total_s, tempo_alvo_s))

        resultados.append([
            instancia, repeticao, semente, tau[0], tau[1], iteracoes, parada,
            otimo, custo, tempo_melhor_s, tempo_total_s, tempo_alvo_s
        ])

        if menor_custo is None or custo < menor_custo:
            menor_custo = custo
            melhor_historico = historico

        print(f"Execução {repeticao}: custo {custo} | tempo {tempo_total_s:.3f} s")

    salvar_csv(
        f"execucoes_{instancia}.csv",
        ["instancia", "repeticao", "semente", "tau_min", "tau_max",
         "limite_iteracoes", "limite_sem_melhora", "otimo", "melhor_custo",
         "tempo_melhor_s", "tempo_total_s", "tempo_alvo_s"],
        resultados
    )

    salvar_csv(
        f"historico_{instancia}.csv",
        ["iteracao", "melhor_custo", "tempo_s", "custo_atual"],
        melhor_historico[1:]
    )

    gerar_graficos(instancia, otimo, melhor_historico, medicoes_ttt)

    return 

main()