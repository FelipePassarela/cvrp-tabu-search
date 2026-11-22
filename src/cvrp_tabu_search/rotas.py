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
        if self.carga + demanda > self.capacidade:
            return False

        self.aumentar_carga(demanda)
        self.aumentar_rota(cliente)
        return True


def distancia(cliente_a, cliente_b, coordenadas):
    # Os identificadores do arquivo começam em 1.
    x_a, y_a = coordenadas[cliente_a - 1]
    x_b, y_b = coordenadas[cliente_b - 1]

    deslocamento_x = x_b - x_a
    deslocamento_y = y_b - y_a
    euclidiana = (deslocamento_x ** 2 + deslocamento_y ** 2) ** 0.5
    return int(euclidiana + 0.5)


def fit(rota, coordenadas, deposito):
    custo = 0
    anterior = deposito

    for cliente in rota:
        custo += distancia(anterior, cliente, coordenadas)
        anterior = cliente

    return custo + distancia(anterior, deposito, coordenadas)


def solucao_inicial(veiculos, dimensao, capacidade, demandas, deposito):
    frota = [Veiculo(capacidade) for _ in range(veiculos)]

    def demanda_cliente(cliente):
        return demandas[cliente - 1]

    clientes = sorted(
        (cliente for cliente in range(1, dimensao + 1) if cliente != deposito),
        key=demanda_cliente,
        reverse=True,
    )

    for cliente in clientes:
        demanda = demanda_cliente(cliente)
        for veiculo in frota:
            if veiculo.adicionar_cliente(cliente, demanda):
                break
        else:
            return None

    return frota


def copiar_rotas(frota):
    return [veiculo.rota.copy() for veiculo in frota]


def inverter(rota, inicio, fim):
    nova_rota = rota.copy()
    trecho = nova_rota[inicio:fim + 1]
    trecho.reverse()
    nova_rota[inicio:fim + 1] = trecho
    return nova_rota
