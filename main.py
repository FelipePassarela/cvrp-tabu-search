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

def melhor_vizinho(frota, custo_total, coordenadas, deposito):
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

                if custo is None or possivel_custo < custo:
                    custo = possivel_custo
                    movimento = (id_veiculo, inicio, fim, nova_rota, custo)

    return movimento

def tabu(list_tabu, novo):
    pass
    # Quando for usar a lista tabu, da pra usar o in para verificar se o elemento esta la

def liberar_tabu(list_tabu):
    pass

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
                coordenadas.append([int(posi1), int(posi2)])
            elif secao == "DEMAND_SECTION":
                demanda = lista_aux[1]
                demandas.append(int(demanda))
            elif secao == "DEPOT_SECTION":
                if "-1" in lista_aux:
                    secao = ""
                    continue
                deposito = int(lista_aux[0])

    return veiculos, dimensao, capacidade, coordenadas, demandas, deposito

def main():
    arquivo = "instacias/A-n33-k5.vrp"
    veiculos, dimensao, capacidade, coordenadas, demandas, deposito = leitura(arquivo)

    print(distancia(1,2, coordenadas))
    print(fit([2,3], coordenadas, deposito))

    return 

main()