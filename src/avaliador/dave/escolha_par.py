"""Escolha no par: dos dois segues de um par, qual a pessoa preferiu, e o previsor aponta o mesmo?

Cada participante avaliou os DOIS segues de cada par (a mesma música inicial; um do Dave, um da
The Chain), na mesma sessão. Para cada (participante, par) e cada métrica, a preferência é a
diferença de notas Dave − The Chain. Nessa diferença, o "jeito" da pessoa (quem dá nota alta para
tudo) se cancela: só sobra qual dos dois ela achou melhor.

O mesmo vale para a LLM: no teste de treino e teste, os dois segues do par de teste recebem o
MESMO histórico e o mesmo perfil; se a LLM só copia o nível da pessoa, a diferença zera. A
preferência é derivada de duas notas pedidas separadamente (a LLM não viu os dois segues juntos).

Medidas, por métrica, entre os pares em que a pessoa NÃO empatou:
- correlacao_%: Pearson entre a diferença humana e a do previsor (empates do previsor entram como
  0); IC 95% por bootstrap de participantes. É a medida principal.
- acordo_%: entre os pares em que o previsor também não empatou, quantas vezes aponta o mesmo
  vencedor (acaso = 50%).
- empate_%: quantas vezes o previsor empata (não escolhe).
Referência humana: outro_humano = média das diferenças dos OUTROS participantes no mesmo par.
Só entram pares vistos por 2 ou mais participantes, para todos usarem as mesmas linhas.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..comum.correlacao import pearson
from .dados import METRICAS

MEDIA = "media_8"


def _por_par(tabela: pd.DataFrame, chaves: list[str]) -> pd.DataFrame:
    """Diferença Dave − The Chain por (chaves..., segue_idx), uma coluna por métrica."""
    larga = tabela.pivot_table(index=chaves + ["segue_idx"], columns="sistema", values=METRICAS,
                               dropna=False)
    dif = pd.DataFrame({m: larga[(m, "dave")] - larga[(m, "the_chain")] for m in METRICAS})
    return dif.reset_index()


def diferencas_humanas(notas: pd.DataFrame) -> pd.DataFrame:
    return _por_par(notas, ["usuario"])


def outro_humano(notas: pd.DataFrame) -> pd.DataFrame:
    """Para cada (participante, par), a média das diferenças dos outros participantes no par."""
    h = diferencas_humanas(notas)
    saida = h[["usuario", "segue_idx"]].copy()
    for m in METRICAS:
        g = h.groupby("segue_idx")[m]
        n = g.transform("count") - h[m].notna()
        saida[m] = ((g.transform("sum") - h[m].fillna(0)) / n.where(n > 0)).to_numpy(float)
    return saida


def diferencas_previstas(previsao: pd.DataFrame) -> pd.DataFrame:
    """Diferenças de um previsor: por participante (se tiver `usuario`) ou por par (ex.: E0)."""
    chaves = ["usuario"] if "usuario" in previsao.columns else []
    return _por_par(previsao, chaves)


def comparar(notas: pd.DataFrame, previsores: dict[str, pd.DataFrame], reamostragens: int = 1000,
             semente: int = 2026) -> pd.DataFrame:
    """Correlação, acordo e empates de cada previsor com as preferências humanas no par.
    `previsores`: tabelas de notas previstas (colunas METRICAS), por linha ou por segue."""
    h = diferencas_humanas(notas)
    base = h.merge(outro_humano(notas), on=["usuario", "segue_idx"], suffixes=("", "__outro_humano"))
    nomes = ["outro_humano"]
    for nome, p in previsores.items():
        d = diferencas_previstas(p)
        chaves = [c for c in ["usuario", "segue_idx"] if c in d.columns]
        d = d.rename(columns={m: f"{m}__{nome}" for m in METRICAS})
        base = base.merge(d, on=chaves, how="left")
        nomes.append(nome)

    dados = {}
    for m in METRICAS:
        colunas = [m] + [f"{m}__{n}" for n in nomes]
        d = base.dropna(subset=colunas)
        d = d[d[m] != 0].reset_index(drop=True)              # a pessoa escolheu um dos dois
        usuarios = d["usuario"].to_numpy()
        dados[m] = {"real": d[m].to_numpy(float), "prev": {n: d[f"{m}__{n}"].to_numpy(float) for n in nomes},
                    "idx_u": {u: np.flatnonzero(usuarios == u) for u in np.unique(usuarios)}}

    def medir(dd: dict, idx) -> dict:
        real = dd["real"][idx]
        saida = {}
        for n in nomes:
            prev = dd["prev"][n][idx]
            decidiu = prev != 0
            saida[n] = {
                "correlacao": np.nan_to_num(pearson(real, prev)),
                "acordo": float(np.mean(np.sign(real[decidiu]) == np.sign(prev[decidiu]))) if decidiu.any() else np.nan,
                "empate": float(np.mean(~decidiu)),
            }
        return saida

    pontos = {m: medir(dd, np.arange(len(dd["real"]))) for m, dd in dados.items()}
    pontos[MEDIA] = {n: {k: float(np.nanmean([pontos[m][n][k] for m in METRICAS]))
                         for k in ("correlacao", "acordo", "empate")} for n in nomes}

    todos = np.unique(base["usuario"])
    rng = np.random.default_rng(semente)
    boot = {m: {n: [] for n in nomes} for m in METRICAS + [MEDIA]}
    for _ in range(reamostragens):
        sorteados = rng.choice(todos, len(todos))
        soma = {n: [] for n in nomes}
        for m, dd in dados.items():
            idx = np.concatenate([dd["idx_u"][u] for u in sorteados if u in dd["idx_u"]])
            r = medir(dd, idx)
            for n in nomes:
                boot[m][n].append(r[n]["correlacao"])
                soma[n].append(r[n]["correlacao"])
        for n in nomes:
            boot[MEDIA][n].append(np.mean(soma[n]))

    linhas = []
    for m in METRICAS + [MEDIA]:
        for n in nomes:
            v = pontos[m][n]
            linhas.append({"metrica": m, "previsor": n, "correlacao_%": 100 * v["correlacao"],
                           "ic_inf_%": 100 * np.percentile(boot[m][n], 2.5),
                           "ic_sup_%": 100 * np.percentile(boot[m][n], 97.5),
                           "acordo_%": 100 * v["acordo"], "empate_%": 100 * v["empate"],
                           "pares": len(dados[m]["real"]) if m in dados else None})
    return pd.DataFrame(linhas)
