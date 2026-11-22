import random
from dataclasses import dataclass
from time import perf_counter

from .rotas import copiar_rotas, fit, inverter


@dataclass(frozen=True)
class ParametrosBusca:
    iteracoes: int
    parada: int
    tau: tuple[int, int] = (3, 7)


class ProgressoBusca:
    def __init__(self, frota, coordenadas, deposito, inicio_execucao):
        self.melhores_rotas = copiar_rotas(frota)
        self.melhor_custo = sum(
            fit(rota, coordenadas, deposito) for rota in self.melhores_rotas
        )
        self.iteracoes_sem_melhora = 0
        self.historico = []
        self._inicio_execucao = inicio_execucao
        self._registrar_custo(0, self.melhor_custo)

    def registrar_iteracao(self, iteracao, frota, custo_atual):
        if custo_atual < self.melhor_custo:
            self.melhor_custo = custo_atual
            self.melhores_rotas = copiar_rotas(frota)
            self.iteracoes_sem_melhora = 0
        else:
            self.iteracoes_sem_melhora += 1

        self._registrar_custo(iteracao, custo_atual)

    def resultado(self):
        return self.melhores_rotas, self.melhor_custo, self.historico

    def _registrar_custo(self, iteracao, custo_atual):
        tempo_s = perf_counter() - self._inicio_execucao
        self.historico.append((iteracao, self.melhor_custo, tempo_s, custo_atual))


def avaliar_inversoes(rota, coordenadas, deposito, custo_sem_rota):
    for inicio in range(len(rota) - 1):
        for fim in range(inicio + 1, len(rota)):
            nova_rota = inverter(rota, inicio, fim)
            custo = custo_sem_rota + fit(nova_rota, coordenadas, deposito)
            primeiro, ultimo = rota[inicio], rota[fim]
            extremos = (min(primeiro, ultimo), max(primeiro, ultimo))
            yield inicio, fim, nova_rota, custo, extremos


def movimento_bloqueado(lista_tabu, chave, iteracao, custo, melhor_custo):
    bloqueado = iteracao <= lista_tabu.get(chave, 0)
    return bloqueado and custo >= melhor_custo


def registrar_movimento_tabu(lista_tabu, chaves, iteracao, tau):
    fim_bloqueio = iteracao + random.randint(*tau)
    for chave in chaves:
        lista_tabu[chave] = fim_bloqueio
