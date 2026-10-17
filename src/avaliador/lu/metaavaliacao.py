"""Meta-avaliação em 3 níveis (Zhang et al., 2024).

- Conjunto (dataset): correlação entre todas as notas.
- Usuário: correlação dentro das explicações de cada usuário, depois média entre usuários.
- Par: correlação dentro de cada par (usuário, filme), depois média entre pares.

Grupos em que uma das séries é constante não têm correlação definida e ficam de fora da média,
como acontece com pandas.Series.mean() no código original.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..comum.correlacao import correlacao as _correlacao
from ..comum.correlacao import pearson_ic

NIVEIS = ["dataset", "user", "pair"]


def _media_por_grupo(df: pd.DataFrame, chaves, real: str, pred: str, metodo: str) -> tuple[float, int]:
    valores = [
        _correlacao(g[real], g[pred], metodo) for _, g in df.groupby(chaves, sort=False)
    ]
    valores = np.array(valores, dtype=float)
    validos = valores[~np.isnan(valores)]
    return (float(validos.mean()) if len(validos) else np.nan), int(len(validos))


def correlacao_3_niveis(df: pd.DataFrame, real: str, pred: str, metodo: str = "pearson") -> dict:
    """Correlação entre a coluna `real` (nota do usuário) e `pred` (nota do avaliador) nos 3 níveis."""
    conjunto = _correlacao(df[real], df[pred], metodo)
    usuario, n_usuarios = _media_por_grupo(df, ["user"], real, pred, metodo)
    par, n_pares = _media_por_grupo(df, ["user", "movie_id"], real, pred, metodo)
    return {
        "dataset": conjunto,
        "user": usuario,
        "pair": par,
        "n_users_validos": n_usuarios,
        "n_pairs_validos": n_pares,
    }


def tabela(df: pd.DataFrame, avaliadores: dict[str, str], aspectos, metodo: str = "pearson") -> pd.DataFrame:
    """Tabela no formato da Tabela 1 de Zhang et al.: uma linha por avaliador, colunas aspecto x nível (em %).

    `avaliadores` mapeia o nome exibido para o prefixo das colunas de nota, por exemplo
    {"Annotator-1": "anot1"} usa as colunas anot1_<aspecto>.
    """
    linhas = []
    for nome, prefixo in avaliadores.items():
        linha = {"avaliador": nome}
        for aspecto in aspectos:
            r = correlacao_3_niveis(df, f"user_{aspecto}", f"{prefixo}_{aspecto}", metodo)
            for nivel in NIVEIS:
                linha[(aspecto, nivel)] = 100 * r[nivel]
        for nivel in NIVEIS:
            linha[("average", nivel)] = np.nanmean([linha[(a, nivel)] for a in aspectos])
        linhas.append(linha)
    out = pd.DataFrame(linhas).set_index("avaliador")
    out.columns = pd.MultiIndex.from_tuples(out.columns, names=["aspecto", "nivel"])
    return out


def dentro_do_tipo(df: pd.DataFrame, avaliadores: dict[str, str], aspectos) -> pd.Series:
    """Pearson médio (%) calculado DENTRO de cada tipo de explicação e depois promediado.

    Remove a parte da correlação que vem só de acertar qual tipo de explicação é melhor.
    O que sobra é a capacidade de distinguir explicações do MESMO tipo (o texto em si, o filme, o usuário).
    """
    saida = {}
    for nome, prefixo in avaliadores.items():
        valores = [
            _correlacao(g[f"user_{a}"], g[f"{prefixo}_{a}"], "pearson")
            for a in aspectos
            for _, g in df.groupby("explanation_type")
        ]
        saida[nome] = 100 * np.nanmean(valores)
    return pd.Series(saida, name="pearson_dentro_do_tipo_%")


def bootstrap_usuarios(
    df: pd.DataFrame,
    avaliadores: dict[str, str],
    aspectos,
    referencia: dict[str, str] | None = None,
    reamostragens: int = 1000,
    semente: int = 2026,
) -> pd.DataFrame:
    """Intervalo de confiança de 95% da correlação de Pearson média (nível conjunto), por bootstrap.

    Reamostra USUÁRIOS com reposição (não explicações), porque as explicações de um mesmo usuário
    não são independentes. Para cada avaliador, devolve a média nos 4 aspectos e o intervalo.

    `referencia` mapeia avaliador -> avaliador de comparação (por exemplo, cada condição contra o
    E0 do mesmo modelo). Nesse caso, também calcula a diferença pareada e seu intervalo: se o
    intervalo não contém zero, a diferença dificilmente é acaso.
    """
    rng = np.random.default_rng(semente)
    usuarios = df["user"].unique()
    indices = {u: np.flatnonzero(df["user"].values == u) for u in usuarios}
    reais = {a: df[f"user_{a}"].to_numpy(float) for a in aspectos}
    preds = {n: {a: df[f"{p}_{a}"].to_numpy(float) for a in aspectos} for n, p in avaliadores.items()}

    def media_pearson(idx, nome):
        valores = [_correlacao(reais[a][idx], preds[nome][a][idx], "pearson") for a in aspectos]
        return np.nanmean(valores) * 100

    amostras = {n: [] for n in avaliadores}
    diferencas = {n: [] for n in (referencia or {})}
    for _ in range(reamostragens):
        sorteio = rng.choice(usuarios, size=len(usuarios), replace=True)
        idx = np.concatenate([indices[u] for u in sorteio])
        valores = {n: media_pearson(idx, n) for n in avaliadores}
        for n, v in valores.items():
            amostras[n].append(v)
        for n, ref in (referencia or {}).items():
            diferencas[n].append(valores[n] - valores[ref])

    todos = np.arange(len(df))
    linhas = []
    for n in avaliadores:
        a = np.array(amostras[n])
        linha = {"avaliador": n, "media_%": media_pearson(todos, n),
                 "ic95_inf": np.nanpercentile(a, 2.5), "ic95_sup": np.nanpercentile(a, 97.5)}
        if referencia and n in referencia:
            d = np.array(diferencas[n])
            linha.update({"comparado_com": referencia[n],
                          "diferenca": media_pearson(todos, n) - media_pearson(todos, referencia[n]),
                          "dif_ic95_inf": np.nanpercentile(d, 2.5),
                          "dif_ic95_sup": np.nanpercentile(d, 97.5)})
        linhas.append(linha)
    return pd.DataFrame(linhas).set_index("avaliador")


def tabela_pearson_ic(
    df: pd.DataFrame,
    avaliadores: dict[str, str],
    aspectos,
    confianca: float = 0.95,
    reamostragens: int = 1000,
    semente: int = 2026,
) -> pd.DataFrame:
    """Pearson no nível do conjunto, por avaliador e aspecto, com p-valor e dois intervalos.

    - `ic_fisher`: o intervalo do scipy.stats.pearsonr (transformação de Fisher). Supõe que as
      2.536 explicações são independentes, o que não é verdade: cada usuário avaliou ~65.
    - `ic_boot`: bootstrap reamostrando USUÁRIOS, que respeita essa dependência.
    Os dois lado a lado mostram o quanto a fórmula de Fisher subestima a incerteza aqui.
    """
    rng = np.random.default_rng(semente)
    usuarios = df["user"].unique()
    indices = {u: np.flatnonzero(df["user"].values == u) for u in usuarios}
    sorteios = [np.concatenate([indices[u] for u in rng.choice(usuarios, len(usuarios))])
                for _ in range(reamostragens)]
    cauda = 100 * (1 - confianca) / 2

    linhas = []
    for nome, prefixo in avaliadores.items():
        for aspecto in aspectos:
            real = df[f"user_{aspecto}"].to_numpy(float)
            pred = df[f"{prefixo}_{aspecto}"].to_numpy(float)
            r = pearson_ic(real, pred, confianca)
            boot = [_correlacao(real[i], pred[i], "pearson") for i in sorteios]
            linhas.append({
                "avaliador": nome, "aspecto": aspecto, "pearson_%": 100 * r.r, "p": r.p,
                "ic_fisher_inf_%": 100 * r.ic_inf, "ic_fisher_sup_%": 100 * r.ic_sup,
                "ic_boot_inf_%": 100 * np.nanpercentile(boot, cauda),
                "ic_boot_sup_%": 100 * np.nanpercentile(boot, 100 - cauda), "n": r.n,
            })
    return pd.DataFrame(linhas)
