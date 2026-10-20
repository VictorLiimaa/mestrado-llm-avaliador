"""Gráficos do teste de treino e teste do Dave (lê o comparacao.csv do dave_04_treino_teste.py).

1. resumo.png: média dos 8 critérios, por previsor, com IC 95%. Dois painéis com a mesma escala:
   correlação com a nota e correlação dentro do participante.
2. por_criterio.png: os mesmos dois painéis, critério a critério, para os previsores principais.

Cores pelo tipo de previsor: cinza = sem LLM, azul = LLM sem perfil (E0), laranja = LLM com o
histórico do participante. Os previsores com LLM aparecem quando o cache existe.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .dados import METRICAS
from .treino_teste import MEDIA

CRITERIOS = {
    "likeable": "Gostei", "high_quality": "Alta qualidade", "understandable": "Entendi a conexão",
    "sparked_interest": "Despertou interesse", "funny": "Engraçado", "informative": "Informativo",
    "creative": "Criativo", "well_written": "Bem escrito",
}
BASES = {
    "media_usuario": "Média do próprio participante\n(nos outros pares)",
    "outro_humano": "Outro participante\n(mesmo segue)",
    "usuario_mais_segue": "Participante + outro participante",
}
MODELOS = {"qwen2.5-7b": "Qwen", "llama3.1-8b": "Llama", "media-qwen-llama": "Qwen + Llama", "mock": "Mock"}
CONDICOES = {"E0": "sem perfil", "historico": "com histórico", "perfil": "com perfil musical",
             "familiaridade": "com familiaridade", "perfil_familiaridade": "com perfil e familiaridade",
             "completo": "com tudo (histórico, perfil e familiaridade)"}
# Previsores que já contêm a média do participante: dentro do participante eles ficam negativos
# por construção, então não entram nesse painel.
SO_BRUTA = {"media_usuario", "usuario_mais_segue"}

TINTA, TINTA_2, GRADE = "#0b0b0b", "#52514e", "#e4e3df"
# Cinza = sem LLM; azul = LLM sem perfil; laranja = LLM com qualquer informação sobre o participante.
COR = {"base": "#8d8b84", "E0": "#2a78d6"}
COR_ENRIQUECIDA = "#eb6834"


def _num(v: float) -> str:
    return f"{v:.1f}".replace(".", ",")


def _tipo(previsor: str) -> str:
    return previsor.split("__")[1] if "__" in previsor else "base"


def _rotulo(previsor: str) -> str:
    if previsor in BASES:
        return BASES[previsor]
    modelo, condicao = previsor.split("__")
    return f"{MODELOS.get(modelo, modelo)}, {CONDICOES.get(condicao, condicao)}"


def _fonte() -> str:
    """A primeira fonte instalada da lista (Inter no Linux; Arial no Windows), sem avisos."""
    from matplotlib import font_manager
    instaladas = {f.name for f in font_manager.fontManager.ttflist}
    return next((f for f in ("Inter", "Arial", "Helvetica") if f in instaladas), "DejaVu Sans")


def _estilo(plt):
    plt.rcParams.update({
        "font.family": _fonte(), "font.size": 10, "axes.edgecolor": GRADE,
        "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA, "axes.linewidth": 0.8,
        "xtick.major.size": 0, "ytick.major.size": 0, "figure.facecolor": "white",
    })


def _eixo(ax, titulo: str, x_min: float, x_max: float):
    ax.set_title(titulo, loc="left", fontsize=10.5, color=TINTA, fontweight="bold", pad=10)
    ax.axvline(0, color=TINTA_2, lw=0.8, zorder=1)
    ax.grid(axis="x", color=GRADE, lw=0.8, zorder=0)
    ax.set_xlim(x_min, x_max)
    ax.set_xlabel("Pearson (%)")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)


def _titulo_resumo(media: pd.DataFrame) -> str:
    """O título diz o achado, calculado dos números (para continuar certo quando eles mudarem)."""
    llm = [p for p in media.index if _tipo(p) != "base"]
    if not llm:
        return "Previsores sem LLM no teste de treino e teste"
    melhor = max(llm, key=lambda p: media.loc[p, "pearson_%"])
    ref = media.loc["media_usuario", "pearson_%"]
    v = media.loc[melhor, "pearson_%"]
    if v > ref:
        return f"{_rotulo(melhor)} supera a média do próprio participante ({_num(v)}% contra {_num(ref)}%)"
    return (f"A média do próprio participante ({_num(ref)}%) prevê melhor que a melhor LLM "
            f"({_rotulo(melhor)}, {_num(v)}%)")


def grafico_resumo(tabela: pd.DataFrame, arquivo: str | Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _estilo(plt)

    media = tabela[tabela["metrica"] == MEDIA].set_index("previsor")
    # Com muitas condições, mostra só a média dos modelos (se houver), para o gráfico caber.
    combinados = [p for p in media.index if _tipo(p) != "base" and p.startswith("media-")]
    if combinados and len(media) > 9:
        media = media.loc[[p for p in media.index if _tipo(p) == "base" or p in combinados]]
    ordem = [p for p in media.index if _tipo(p) == "base"] + \
            [p for p in media.index if _tipo(p) == "E0"] + \
            [p for p in media.index if _tipo(p) not in ("base", "E0")]
    y = {p: i for i, p in enumerate(reversed(ordem))}
    paineis = [("pearson_%", "ic_inf_%", "ic_sup_%", "Correlação com a nota"),
               ("centrada_%", "centrada_ic_inf_%", "centrada_ic_sup_%",
                "Dentro do participante (sem o \"jeito\" da pessoa)")]
    valores = [media.loc[p, c] for p in ordem for c in ("ic_inf_%", "ic_sup_%")] + \
              [media.loc[p, c] for p in ordem if p not in SO_BRUTA for c in ("centrada_ic_inf_%", "centrada_ic_sup_%")]
    x_min, x_max = min(0, min(valores)) - 3, max(valores) + 9

    fig, eixos = plt.subplots(1, 2, figsize=(11, 0.55 * len(ordem) + 2.2), sharey=True)
    for ax, (col, inf, sup, titulo) in zip(eixos, paineis):
        _eixo(ax, titulo, x_min, x_max)
        for p in ordem:
            if col == "centrada_%" and p in SO_BRUTA:
                ax.text(0.8, y[p], "não se aplica", va="center", fontsize=9, color=TINTA_2)
                continue
            v, a, b = media.loc[p, [col, inf, sup]]
            cor = COR.get(_tipo(p), COR_ENRIQUECIDA)
            ax.plot([a, b], [y[p], y[p]], color=cor, lw=2, solid_capstyle="round", zorder=2)
            ax.scatter([v], [y[p]], s=60, color=cor, edgecolor="white", linewidth=1.5, zorder=3)
            ax.text(b + 1, y[p], _num(v), va="center", fontsize=9.5, color=TINTA)
    eixos[0].set_yticks(list(y.values()), [_rotulo(p) for p in y])
    fig.suptitle(_titulo_resumo(media), x=0.01, ha="left", fontsize=12, color=TINTA, fontweight="bold")
    fig.text(0.01, 0.005, "Média dos 8 critérios do teste do Dave; barras = IC 95% por bootstrap de "
             "participantes. \"Não se aplica\": o previsor já contém a média do participante.",
             fontsize=8.5, color=TINTA_2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.965))
    arquivo = Path(arquivo)
    fig.savefig(arquivo, dpi=200)
    plt.close(fig)
    return arquivo


def grafico_por_criterio(tabela: pd.DataFrame, arquivo: str | Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _estilo(plt)

    previsores = set(tabela["previsor"])

    def melhor(condicao: str):
        for nome in ("media-qwen-llama", "qwen2.5-7b", "llama3.1-8b", "mock"):
            if f"{nome}__{condicao}" in previsores:
                return f"{nome}__{condicao}"
        return None

    series = [p for p in ["media_usuario", "outro_humano", melhor("E0"), melhor("completo") or melhor("historico")] if p]
    marcador = {"media_usuario": "s", "outro_humano": "D"}
    cor = {"media_usuario": "#8d8b84", "outro_humano": TINTA_2}
    linhas = tabela[tabela["metrica"] != MEDIA]
    y = {m: i for i, m in enumerate(reversed(METRICAS))}
    desloc = {p: 0.22 - 0.44 * i / max(len(series) - 1, 1) for i, p in enumerate(series)}
    valores = pd.concat([linhas["pearson_%"], linhas.loc[~linhas["previsor"].isin(SO_BRUTA), "centrada_%"]])
    x_min, x_max = min(0, valores.min()) - 4, valores.max() + 4

    fig, eixos = plt.subplots(1, 2, figsize=(11, 5.6), sharey=True)
    for ax, col, titulo in zip(eixos, ["pearson_%", "centrada_%"],
                               ["Correlação com a nota", "Dentro do participante"]):
        _eixo(ax, titulo, x_min, x_max)
        for m in METRICAS:
            ax.axhline(y[m], color=GRADE, lw=0.6, zorder=0)
        for p in series:
            if col == "centrada_%" and p in SO_BRUTA:
                continue
            d = linhas[linhas["previsor"] == p].set_index("metrica")
            ax.scatter([d.loc[m, col] for m in METRICAS], [y[m] + desloc[p] for m in METRICAS],
                       s=46, marker=marcador.get(p, "o"), color=cor.get(p, COR.get(_tipo(p), COR_ENRIQUECIDA)),
                       edgecolor="white", linewidth=1.2, zorder=3,
                       label=_rotulo(p).replace("\n", " ") if col == "pearson_%" else None)
    eixos[0].set_yticks(list(y.values()), [CRITERIOS[m] for m in y])
    fig.legend(loc="upper left", bbox_to_anchor=(0.01, 0.93), ncol=2, frameon=False,
               fontsize=9, handletextpad=0.3, columnspacing=1.4)
    fig.suptitle("Critério a critério: quanto cada previsor acerta", x=0.01, ha="left",
                 fontsize=12, color=TINTA, fontweight="bold")
    fig.text(0.01, 0.005, "Pearson (%) com a nota de cada participante no teste do Dave. A média do "
             "participante não aparece à direita: ela já contém o \"jeito\" da pessoa.",
             fontsize=8.5, color=TINTA_2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.85))
    arquivo = Path(arquivo)
    fig.savefig(arquivo, dpi=200)
    plt.close(fig)
    return arquivo


def gerar(tabela: pd.DataFrame, pasta: str | Path) -> list[Path]:
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    return [grafico_resumo(tabela, pasta / "resumo.png"),
            grafico_por_criterio(tabela, pasta / "por_criterio.png")]
