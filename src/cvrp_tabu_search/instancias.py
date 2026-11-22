from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Instancia:
    nome: str
    otimo: int
    veiculos: int
    dimensao: int
    capacidade: int
    coordenadas: list[list[float]]
    demandas: list[int]
    deposito: int


def carregar_instancia_padrao():
    nome = "A-n32-k5"
    otimo = 784
    arquivo = Path(__file__).with_name("data") / f"{nome}.vrp"
    return Instancia(nome, otimo, *leitura(arquivo))


def leitura(arquivo):
    with open(arquivo, encoding="utf-8") as entrada:
        cabecalho, secoes = _separar_secoes(entrada)

    nome = cabecalho.get("NAME", "k0")
    sufixo_nome = nome.rsplit("-", 1)[-1]
    veiculos = int(sufixo_nome.rsplit("k", 1)[-1])
    dimensao = int(cabecalho.get("DIMENSION", 0))
    capacidade = int(cabecalho.get("CAPACITY", 0))

    coordenadas = [
        [float(x), float(y)] for _, x, y in secoes["NODE_COORD_SECTION"]
    ]
    demandas = [int(linha[1]) for linha in secoes["DEMAND_SECTION"]]
    deposito = _ler_deposito(secoes["DEPOT_SECTION"])
    return veiculos, dimensao, capacidade, coordenadas, demandas, deposito


def _separar_secoes(arquivo):
    cabecalho = {}
    secoes = {"NODE_COORD_SECTION": [], "DEMAND_SECTION": [], "DEPOT_SECTION": []}
    secao_atual = None

    for linha in arquivo:
        if "EOF" in linha:
            break

        texto = linha.strip()
        if texto in secoes:
            secao_atual = texto
        elif secao_atual is not None:
            secoes[secao_atual].append(texto.split())
        elif ":" in texto:
            campo, valor = texto.split(":", 1)
            cabecalho[campo.strip()] = valor.strip()

    return cabecalho, secoes


def _ler_deposito(linhas):
    deposito = 0
    for linha in linhas:
        if "-1" in linha:
            break
        deposito = int(linha[0])

    return deposito
