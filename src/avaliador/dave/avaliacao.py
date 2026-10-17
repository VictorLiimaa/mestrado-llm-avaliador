"""Comparação entre o ouvinte simulado (LLM) e os participantes reais do teste do Dave.

Três perguntas, da mais importante para a menos:

1. Conclusões: a LLM chega às mesmas conclusões do artigo? Para cada métrica, comparamos a
   diferença Dave - The Chain (no geral, nos segues informativos e nos engraçados).
2. Ranking de segues: a LLM ordena os segues como a média dos participantes? Correlação no
   nível do segue, com um teto humano: o quanto UM participante concorda com a média dos outros.
3. Escolha no par: em cada par (mesma música inicial), a LLM escolhe o mesmo vencedor que cada
   participante?
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..comum.correlacao import pearson, pearson_ic, spearman
from ..comum.estatistica import estrelas, ttest_independente, ttest_pareado
from .dados import METRICAS

GRUPOS = {"geral": None, "informativos": "I", "engracados": "F"}


# ---------------------------------------------------------------- 0. tabelas do artigo
def tabela_artigo(notas: pd.DataFrame) -> pd.DataFrame:
    """Reproduz as tabelas do artigo a partir das notas humanas, como no notebook dos autores.

    geral: teste t pareado (ttest_rel) entre as linhas do Dave e da The Chain;
    informativos / engracados: teste t independente (ttest_ind) dentro da categoria.
    """
    linhas = []
    for grupo, cat in GRUPOS.items():
        df = notas if cat is None else notas[notas["categoria"] == cat]
        for m in METRICAS:
            if cat is None:
                pares = df.pivot_table(index=["usuario", "segue_idx"], columns="sistema", values=m)
                pares = pares.dropna()
                t, p = ttest_pareado(pares["dave"], pares["the_chain"])
                md, mc = df[df.sistema == "dave"][m].mean(), df[df.sistema == "the_chain"][m].mean()
            else:
                a, b = df[df.sistema == "dave"][m], df[df.sistema == "the_chain"][m]
                t, p = ttest_independente(a, b)
                md, mc = a.mean(), b.mean()
            linhas.append({"grupo": grupo, "metrica": m, "dave": md, "the_chain": mc, "t": t, "p": p})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- 1. conclusões
def conclusoes(notas: pd.DataFrame, segues: pd.DataFrame, llm: pd.DataFrame) -> pd.DataFrame:
    """Diferença Dave - The Chain para humanos e para a LLM, no nível do segue.

    Os dois lados usam a mesma unidade (o segue) e o mesmo teste, para a comparação ser justa:
    humanos = média dos participantes que viram aquele segue; LLM = nota da LLM.
    geral: pareado por música inicial; categorias: independente, como no artigo.
    """
    humanos = notas.groupby(["segue_idx", "sistema"])[METRICAS].mean().reset_index()
    base = segues[["segue_idx", "sistema", "categoria"]]
    fontes = {"humanos": base.merge(humanos, on=["segue_idx", "sistema"]),
              "llm": base.merge(llm, on=["segue_idx", "sistema"])}
    linhas = []
    for grupo, cat in GRUPOS.items():
        for m in METRICAS:
            linha = {"grupo": grupo, "metrica": m}
            for nome, df in fontes.items():
                if cat is None:
                    w = df.pivot_table(index="segue_idx", columns="sistema", values=m).dropna()
                    dif = (w["dave"] - w["the_chain"]).mean()
                    _, p = ttest_pareado(w["dave"], w["the_chain"])
                else:
                    d = df[df.categoria == cat]
                    a, b = d[d.sistema == "dave"][m], d[d.sistema == "the_chain"][m]
                    dif = a.mean() - b.mean()
                    _, p = ttest_independente(a, b)
                linha[f"dif_{nome}"] = dif
                linha[f"p_{nome}"] = p
            linha["mesmo_sinal"] = np.sign(linha["dif_humanos"]) == np.sign(linha["dif_llm"])
            sig_h, sig_l = linha["p_humanos"] < 0.05, linha["p_llm"] < 0.05
            linha["mesma_conclusao"] = (sig_h == sig_l) and (not sig_h or linha["mesmo_sinal"])
            linhas.append(linha)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- 2. ranking de segues
def _teto_humano(notas: pd.DataFrame, m: str) -> np.ndarray:
    """Para cada nota humana, a média dos OUTROS participantes que viram o mesmo segue."""
    g = notas.groupby(["segue_idx", "sistema"])[m]
    soma, n = g.transform("sum"), g.transform("count")
    return ((soma - notas[m]) / (n - 1)).to_numpy(float)


def correlacoes(notas: pd.DataFrame, llm: pd.DataFrame, reamostragens: int = 1000,
                semente: int = 2026) -> pd.DataFrame:
    """Correlação (%) entre a nota de cada participante e: (a) a LLM; (b) a média dos outros
    participantes do mesmo segue (o "teto humano"). Só entram segues vistos por 2+ pessoas,
    para os dois avaliadores usarem exatamente as mesmas linhas.

    Dois intervalos de 95%: o de Fisher (o mesmo do scipy.stats.pearsonr, que supõe notas
    independentes) e o de bootstrap por participante (que respeita as várias notas de cada pessoa).
    """
    df = notas.merge(llm, on=["segue_idx", "sistema"], suffixes=("", "_llm"))
    vistos = df.groupby(["segue_idx", "sistema"])["usuario"].transform("count") >= 2
    df = df[vistos].reset_index(drop=True)
    rng = np.random.default_rng(semente)
    usuarios = df["usuario"].unique()
    idx_por_usuario = {u: np.flatnonzero(df["usuario"].values == u) for u in usuarios}

    linhas = []
    for m in METRICAS:
        real = df[m].to_numpy(float)
        preditores = {"llm": df[f"{m}_llm"].to_numpy(float), "outro_humano": _teto_humano(df, m)}
        for nome, pred in preditores.items():
            ok = ~(np.isnan(real) | np.isnan(pred))
            r = pearson_ic(real[ok], pred[ok])
            amostras = []
            for _ in range(reamostragens):
                idx = np.concatenate([idx_por_usuario[u] for u in rng.choice(usuarios, len(usuarios))])
                a, b = real[idx], pred[idx]
                k = ~(np.isnan(a) | np.isnan(b))
                amostras.append(pearson(a[k], b[k]))
            linhas.append({"metrica": m, "avaliador": nome, "pearson_%": 100 * r.r, "p": r.p,
                           "ic_fisher_inf_%": 100 * r.ic_inf, "ic_fisher_sup_%": 100 * r.ic_sup,
                           "ic_boot_inf_%": 100 * np.nanpercentile(amostras, 2.5),
                           "ic_boot_sup_%": 100 * np.nanpercentile(amostras, 97.5),
                           "spearman_%": 100 * spearman(real[ok], pred[ok]), "n": r.n})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- 3. escolha no par
def escolha_no_par(notas: pd.DataFrame, llm: pd.DataFrame) -> pd.DataFrame:
    """Em cada par (participante, música inicial), quem ganhou em cada métrica: Dave, The Chain
    ou empate. Mede quantas vezes a LLM escolhe o mesmo vencedor que o participante, entre os
    pares em que NENHUM dos dois deu empate. Referência: 50% seria acaso.
    """
    h = notas.pivot_table(index=["usuario", "segue_idx"], columns="sistema", values=METRICAS)
    l = llm.pivot_table(index="segue_idx", columns="sistema", values=METRICAS)
    linhas = []
    for m in METRICAS:
        dh = (h[(m, "dave")] - h[(m, "the_chain")]).rename("h").reset_index()
        dl = (l[(m, "dave")] - l[(m, "the_chain")]).rename("l").reset_index()
        d = dh.merge(dl, on="segue_idx").dropna()
        sem_empate = d[(d.h != 0) & (d.l != 0)]
        linhas.append({
            "metrica": m,
            "acordo_%": 100 * (np.sign(sem_empate.h) == np.sign(sem_empate.l)).mean(),
            "pares_sem_empate": len(sem_empate),
            "empate_humano_%": 100 * (d.h == 0).mean(),
            "empate_llm_%": 100 * (d.l == 0).mean(),
        })
    return pd.DataFrame(linhas)


def formatar_tabela_artigo(t: pd.DataFrame) -> pd.DataFrame:
    """Formato do artigo: médias com estrelas no vencedor."""
    saida = []
    for _, r in t.iterrows():
        e = estrelas(r["p"])
        d = f"{r['dave']:.2f}" + (e if r["dave"] >= r["the_chain"] else "")
        c = f"{r['the_chain']:.2f}" + (e if r["the_chain"] > r["dave"] else "")
        saida.append({"grupo": r["grupo"], "metrica": r["metrica"], "dave": d, "the_chain": c})
    return pd.DataFrame(saida)
