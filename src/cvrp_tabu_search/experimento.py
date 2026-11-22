import random
from dataclasses import dataclass
from functools import partial
from time import perf_counter

from .relatorios import gerar_relatorios
from .rotas import solucao_inicial

REPETICOES = 5


@dataclass(frozen=True)
class Execucao:
    semente: int
    custo: int
    historico: list[tuple[int, int, float, int]]
    tempo_total_s: float
    tempo_melhor_s: float | None
    tempo_alvo_s: float | None


def executar_experimento(instancia, busca, parametros, *, prefixo=""):
    buscar = partial(
        busca,
        coordenadas=instancia.coordenadas,
        deposito=instancia.deposito,
        tau=parametros.tau,
        iteracoes=parametros.iteracoes,
        parada=parametros.parada,
    )
    execucoes = _executar_repeticoes(instancia, buscar)
    if execucoes is None:
        return

    gerar_relatorios(
        instancia.nome,
        instancia.otimo,
        parametros,
        execucoes,
        prefixo=prefixo,
    )


def _executar_repeticoes(instancia, buscar):
    execucoes = []
    for repeticao in range(1, REPETICOES + 1):
        execucao = _executar_repeticao(instancia, buscar, semente=repeticao)
        if execucao is None:
            print("Impossivel montar a solucao inicial, deu algum b.o aqui")
            return None

        execucoes.append(execucao)
        print(
            f"Execução {repeticao}: custo {execucao.custo}"
            f" | tempo {execucao.tempo_total_s:.3f} s"
        )

    return execucoes


def _executar_repeticao(instancia, buscar, semente):
    random.seed(semente)
    inicio_execucao = perf_counter()
    frota = solucao_inicial(
        instancia.veiculos,
        instancia.dimensao,
        instancia.capacidade,
        instancia.demandas,
        instancia.deposito,
    )
    if frota is None:
        return None

    _, custo, historico = buscar(frota, inicio_execucao=inicio_execucao)
    tempo_total_s = perf_counter() - inicio_execucao
    tempo_melhor_s, tempo_alvo_s = _medir_tempos(historico, custo, instancia.otimo)
    return Execucao(semente, custo, historico, tempo_total_s, tempo_melhor_s, tempo_alvo_s)


def _medir_tempos(historico, custo_final, otimo):
    tempo_melhor_s = None
    tempo_alvo_s = None
    for _, melhor_custo, tempo_s, _ in historico:
        if tempo_melhor_s is None and melhor_custo == custo_final:
            tempo_melhor_s = tempo_s
        if tempo_alvo_s is None and melhor_custo <= otimo:
            tempo_alvo_s = tempo_s
        if tempo_melhor_s is not None and tempo_alvo_s is not None:
            break

    return tempo_melhor_s, tempo_alvo_s
