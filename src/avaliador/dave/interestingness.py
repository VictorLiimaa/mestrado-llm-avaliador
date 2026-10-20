"""A nota do próprio Dave (interestingness) como previsor das notas humanas.

O Dave escolhe o segue com maior interestingness = 0,4 raridade + 0,2 impopularidade + 0,4 concisão
(pesos do artigo, escolhidos "por experimentação empírica"; aprendê-los ficou como trabalho futuro).

1. Reprodução do artigo (`correlacoes_artigo`): Spearman entre a interestingness (e cada componente)
   e as notas dos participantes, nos segues do Dave, separado por categoria. É o único resultado do
   artigo calculado sem pessoas novas. Reproduz o heatmap do notebook dos autores
   (quantitative_analysis.ipynb, "Interestingness and metrics").

2. Experimento offline com treino e teste (`validacao_cruzada`): aprendemos os pesos da fórmula
   com as notas de parte dos segues e medimos nos segues que ficaram de fora. A divisão é por
   segue (validação cruzada em k partes, repetida): um segue de teste nunca foi visto no treino,
   por nenhum participante. Comparamos, nas mesmas notas:
   - pesos_artigo: a fórmula com os pesos do artigo (sem treino);
   - pesos_aprendidos: a mesma fórmula, pesos escolhidos no treino (um conjunto por critério);
   - LLM (E0) e outro_humano, se fornecidos.
   Os pesos são buscados numa grade (somam 1, passo 0,05), maximizando o Spearman no treino, como
   no artigo, em que só a ordem dos segues importa.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..comum.estatistica import p_bicaudal_t
from .dados import METRICAS

COMPONENTES = ["raridade", "impopularidade", "concisao"]
PESOS_ARTIGO = {"raridade": 0.4, "impopularidade": 0.2, "concisao": 0.4}
# As quatro métricas de "valência" do heatmap do artigo.
VALENCIA = ["likeable", "high_quality", "sparked_interest", "understandable"]


def notas_dave(notas: pd.DataFrame, segues: pd.DataFrame) -> pd.DataFrame:
    """Notas humanas dos segues do Dave, com a interestingness e os componentes de cada segue."""
    s = segues[segues["sistema"] == "dave"][["segue_idx", "interestingness"] + COMPONENTES]
    return notas[notas["sistema"] == "dave"].merge(s, on="segue_idx").reset_index(drop=True)


def _postos(x) -> np.ndarray:
    return pd.Series(x).rank(method="average").to_numpy(float)


def _spearman(a, b) -> float:
    a, b = _postos(a), _postos(b)
    a, b = a - a.mean(), b - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den else np.nan


def _p_spearman(rho: float, n: int) -> float:
    """p-valor bicaudal pela aproximação t, a mesma do scipy.stats.spearmanr."""
    if np.isnan(rho) or n < 3:
        return np.nan
    if abs(rho) >= 1:
        return 0.0
    return p_bicaudal_t(rho * np.sqrt((n - 2) / (1 - rho * rho)), n - 2)


# ---------------------------------------------------------------- 1. reprodução do artigo
def correlacoes_artigo(notas: pd.DataFrame, segues: pd.DataFrame, metricas=VALENCIA) -> pd.DataFrame:
    """Spearman entre cada métrica humana e a interestingness / componentes, por categoria."""
    df = notas_dave(notas, segues)
    linhas = []
    for categoria, nome in [("I", "informativos"), ("F", "engracados")]:
        d = df[df["categoria"] == categoria]
        for m in metricas:
            for atributo in ["interestingness"] + COMPONENTES:
                x = d[[m, atributo]].dropna()
                rho = _spearman(x[m], x[atributo])
                linhas.append({"categoria": nome, "metrica": m, "atributo": atributo,
                               "spearman": rho, "p": _p_spearman(rho, len(x)), "n": len(x)})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- 2. pesos aprendidos
def grade_pesos(passo: float = 0.05) -> np.ndarray:
    """Todas as combinações (raridade, impopularidade, concisão) >= 0 que somam 1."""
    k = int(round(1 / passo))
    return np.array([(i / k, j / k, (k - i - j) / k) for i in range(k + 1) for j in range(k + 1 - i)])


def aprender_pesos(componentes: np.ndarray, notas: np.ndarray, grade: np.ndarray) -> np.ndarray:
    """Pesos da grade com maior Spearman entre a fórmula e as notas (empates: o primeiro)."""
    ok = ~np.isnan(notas)
    y = _postos(notas[ok])
    y = y - y.mean()
    escores = componentes[ok] @ grade.T                      # uma coluna por combinação de pesos
    postos = pd.DataFrame(escores).rank(method="average").to_numpy(float, copy=True)
    postos -= postos.mean(axis=0)
    den = np.sqrt((postos ** 2).sum(axis=0) * (y ** 2).sum())
    rho = np.divide(postos.T @ y, den, out=np.full(len(grade), -np.inf), where=den > 0)
    return grade[int(np.argmax(rho))]


def validacao_cruzada(notas: pd.DataFrame, segues: pd.DataFrame,
                      previsores: dict[str, pd.DataFrame] | None = None, categoria: str | None = None,
                      partes: int = 5, repeticoes: int = 10, passo: float = 0.05,
                      reamostragens: int = 1000, semente: int = 2026) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Treino e teste por segue. Devolve (comparacao, pesos).

    comparacao: Spearman (%) de cada previsor com as notas humanas, por métrica e na média das
    métricas (`media_8`), com IC 95% por bootstrap de participantes, e a diferença para os pesos
    do artigo (com IC). Cada nota recebe, dos pesos aprendidos, a média das previsões feitas
    quando o seu segue estava no teste (uma por repetição): tudo fora da amostra de treino.
    pesos: os pesos aprendidos em cada parte e repetição, por métrica.
    Um previsor que dá a mesma nota a todas as linhas tem Spearman indefinido; contamos como 0.
    `previsores`: tabelas com notas previstas (colunas METRICAS) por segue (ex.: a LLM) ou por
    linha (com `usuario`, ex.: outro_humano).
    """
    df = notas_dave(notas, segues)
    if categoria:
        df = df[df["categoria"] == categoria].reset_index(drop=True)
    grade = grade_pesos(passo)
    comp = df[COMPONENTES].to_numpy(float)
    rng = np.random.default_rng(semente)
    lista_segues = df["segue_idx"].unique()

    soma = {m: np.zeros(len(df)) for m in METRICAS}
    vezes = np.zeros(len(df))
    pesos = []
    for rep in range(repeticoes):
        embaralhados = rng.permutation(lista_segues)
        for parte, teste_segues in enumerate(np.array_split(embaralhados, partes)):
            teste = df["segue_idx"].isin(teste_segues).to_numpy()
            vezes[teste] += 1
            for m in METRICAS:
                w = aprender_pesos(comp[~teste], df.loc[~teste, m].to_numpy(float), grade)
                soma[m][teste] += comp[teste] @ w
                pesos.append({"repeticao": rep, "parte": parte, "metrica": m,
                              **dict(zip(COMPONENTES, w))})

    prev = {"pesos_artigo": {m: comp @ np.array([PESOS_ARTIGO[c] for c in COMPONENTES]) for m in METRICAS},
            "pesos_aprendidos": {m: soma[m] / vezes for m in METRICAS}}
    for nome, p in (previsores or {}).items():
        chaves = [c for c in ["usuario", "segue_idx", "sistema"] if c in p.columns]
        x = df[chaves].merge(p[chaves + METRICAS], on=chaves, how="left")
        prev[nome] = {m: x[m].to_numpy(float) for m in METRICAS}
    comparacao = _comparar(df, prev, reamostragens, rng)
    return comparacao, pd.DataFrame(pesos)


def _comparar(df: pd.DataFrame, prev: dict, reamostragens: int, rng) -> pd.DataFrame:
    nomes = list(prev)
    usuarios = df["usuario"].to_numpy()
    todos = np.unique(usuarios)
    idx_u = {u: np.flatnonzero(usuarios == u) for u in todos}

    def medir(idx):
        saida = {}
        for m in METRICAS:
            real = df[m].to_numpy(float)[idx]
            mascara = ~np.isnan(real)
            for n in nomes:
                mascara &= ~np.isnan(prev[n][m][idx])
            # Previsor constante (ex.: a LLM dá a mesma nota a todos) não ordena nada: vale 0,
            # para que a média das 8 métricas use sempre as mesmas 8 parcelas.
            saida[m] = {n: np.nan_to_num(_spearman(real[mascara], prev[n][m][idx][mascara])) for n in nomes}
        saida["media_8"] = {n: float(np.nanmean([saida[m][n] for m in METRICAS])) for n in nomes}
        return saida

    ponto = medir(np.arange(len(df)))
    boot = {m: {n: {"rho": [], "dif": []} for n in nomes} for m in METRICAS + ["media_8"]}
    for _ in range(reamostragens):
        idx = np.concatenate([idx_u[u] for u in rng.choice(todos, len(todos))])
        r = medir(idx)
        for m in boot:
            for n in nomes:
                boot[m][n]["rho"].append(r[m][n])
                boot[m][n]["dif"].append(r[m][n] - r[m]["pesos_artigo"])
    linhas = []
    for m in METRICAS + ["media_8"]:
        for n in nomes:
            ic = lambda t, q: 100 * np.nanpercentile(boot[m][n][t], q)
            linhas.append({"metrica": m, "previsor": n, "spearman_%": 100 * ponto[m][n],
                           "ic_inf_%": ic("rho", 2.5), "ic_sup_%": ic("rho", 97.5),
                           "dif_vs_pesos_artigo_%": 100 * (ponto[m][n] - ponto[m]["pesos_artigo"]),
                           "dif_ic_inf_%": ic("dif", 2.5), "dif_ic_sup_%": ic("dif", 97.5)})
    return pd.DataFrame(linhas)
