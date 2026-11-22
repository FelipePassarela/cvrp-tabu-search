import csv

import matplotlib.pyplot as plt


CABECALHO_EXECUCOES = [
    "instancia", "repeticao", "semente", "tau_min", "tau_max",
    "limite_iteracoes", "limite_sem_melhora", "otimo", "melhor_custo",
    "tempo_melhor_s", "tempo_total_s", "tempo_alvo_s",
]
CABECALHO_HISTORICO = ["iteracao", "melhor_custo", "tempo_s", "custo_atual"]


def gerar_relatorios(instancia, otimo, parametros, execucoes, *, prefixo=""):
    nome = f"{prefixo}{instancia}"
    resultados = _linhas_execucoes(instancia, otimo, parametros, execucoes)
    salvar_csv(f"execucoes_{nome}.csv", CABECALHO_EXECUCOES, resultados)

    melhor_execucao = min(execucoes, key=lambda execucao: execucao.custo)
    melhor_historico = melhor_execucao.historico
    salvar_csv(f"historico_{nome}.csv", CABECALHO_HISTORICO, melhor_historico[1:])

    medicoes_ttt = [(execucao.tempo_total_s, execucao.tempo_alvo_s) for execucao in execucoes]
    gerar_graficos(instancia, otimo, melhor_historico, medicoes_ttt, prefixo=prefixo)


def _linhas_execucoes(instancia, otimo, parametros, execucoes):
    for repeticao, execucao in enumerate(execucoes, start=1):
        yield [
            instancia, repeticao, execucao.semente, *parametros.tau,
            parametros.iteracoes, parametros.parada, otimo, execucao.custo,
            execucao.tempo_melhor_s, execucao.tempo_total_s, execucao.tempo_alvo_s,
        ]


def salvar_csv(caminho, cabecalho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def gerar_graficos(instancia, otimo, melhor_historico, medicoes_ttt, *, prefixo=""):
    plt.style.use("default")
    nome = f"{prefixo}{instancia}"
    _grafico_evolucao(instancia, otimo, melhor_historico, f"evolucao_{nome}.png")
    _grafico_ttt(instancia, otimo, medicoes_ttt, f"ttt_{nome}.png")


def _grafico_evolucao(instancia, otimo, historico, caminho):
    iteracoes = []
    custos = []

    # A posição 0 do histórico é a solução inicial.
    for iteracao, _, _, custo_atual in historico[1:]:
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
    fig.savefig(caminho, dpi=200)
    plt.close(fig)


def _grafico_ttt(instancia, otimo, medicoes_ttt, caminho):
    tempos, porcentagens, acertos = _curva_ttt(medicoes_ttt)
    total = len(medicoes_ttt)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.step(
        tempos, porcentagens, where="post", color="tab:blue",
        label=f"Alvo {otimo}: {acertos} de {total}",
    )
    ax.set_title(f"Time-to-Target — {instancia}")
    ax.set_xlabel("Tempo decorrido (s)")
    ax.set_ylabel("Execuções que atingiram o alvo (%)")
    ax.set_ylim(-4, 104)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.legend()

    fig.tight_layout()
    fig.savefig(caminho, dpi=200)
    plt.close(fig)


def _curva_ttt(medicoes_ttt):
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
    return tempos, porcentagens, len(tempos_alvo)
