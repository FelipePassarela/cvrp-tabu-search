# Talvez caiba fazer uma estrutura ou uma classe para os elementos, dessa forma da pra guardar o tau dentro deles mesmo

"""
K = numero de veiculos
Q = capacidade do veiculo
qi = demanda do cliente i
dij = distancia entre os vertices i e j
xij = variavel que diz se o arco pertence a solucao, 1 caso sim e 0 caso nao
ui = carga acumulada apos atender o cliente i

Fit tem que minimizar a distancia total percorrida
x vai ser uma matriz de tamanho i x j e na posicao i,0 e 0,j vai guardar o valor k

Para avaliar uma solucao: todos os clientes devem ser atendidos, demanda total da rota nao ultrapassa 100, a soma total das distancias eh minimizada

"""

class Veiculo:
    pass

def fit(novo):
    pass

def tabu(list_tabu, novo):
    pass
    # Quando for usar a lista tabu, da pra usar o in para verificar se o elemento esta la

def liberar_tabu(list_tabu):
    pass

def busca(sol_inicial):
    tau = int() 
    melhor_sol = []