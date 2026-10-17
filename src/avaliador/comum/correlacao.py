"""Correlações de Pearson, Spearman e Kendall só com numpy; Pearson também com p-valor e intervalo.

O scipy faz o mesmo, mas no Windows com o "Controle Inteligente de Aplicativos" ligado as DLLs do
scipy são bloqueadas. Os testes conferem que os valores batem com o scipy quando ele está disponível.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

from .estatistica import p_bicaudal_t


def _postos(x: np.ndarray) -> np.ndarray:
    """Postos médios (empates recebem a média das posições), como scipy.stats.rankdata."""
    ordem = np.argsort(x, kind="mergesort")
    postos = np.empty(len(x), dtype=float)
    x_ord = x[ordem]
    inicio = 0
    for i in range(1, len(x) + 1):
        if i == len(x) or x_ord[i] != x_ord[inicio]:
            postos[ordem[inicio:i]] = (inicio + i - 1) / 2 + 1
            inicio = i
    return postos


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    denominador = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / denominador) if denominador else np.nan


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return pearson(_postos(a), _postos(b))


def kendall(a: np.ndarray, b: np.ndarray) -> float:
    """Tau-b de Kendall (com correção para empates), como scipy.stats.kendalltau."""
    da = np.sign(a[:, None] - a[None, :])
    db = np.sign(b[:, None] - b[None, :])
    sup = np.triu_indices(len(a), k=1)
    da, db = da[sup], db[sup]
    concordancia = (da * db).sum()
    denominador = np.sqrt((da != 0).sum() * (db != 0).sum())
    return float(concordancia / denominador) if denominador else np.nan


METODOS = {"pearson": pearson, "spearman": spearman, "kendall": kendall}


def correlacao(a, b, metodo: str = "pearson") -> float:
    """Correlação entre duas séries. NaN se alguma for constante (correlação indefinida)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 2 or np.all(a == a[0]) or np.all(b == b[0]):
        return np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return float(METODOS[metodo](a, b))


@dataclass
class ResultadoPearson:
    """Correlação de Pearson com p-valor e intervalo de confiança, como scipy.stats.pearsonr."""

    r: float
    p: float
    ic_inf: float
    ic_sup: float
    n: int


def pearson_ic(a, b, confianca: float = 0.95) -> ResultadoPearson:
    """Pearson com p-valor bicaudal e intervalo de confiança pela transformação de Fisher.

    Reproduz scipy.stats.pearsonr(a, b) e o seu .confidence_interval(confidence_level):
    - p-valor: teste t com n - 2 graus de liberdade, t = r * sqrt((n - 2) / (1 - r²));
    - intervalo: z = arctanh(r) tem erro padrão 1 / sqrt(n - 3); o intervalo
      z ± z_crítico * erro é levado de volta com tanh. Com n <= 3, o intervalo é [-1, 1].

    Pares com NaN em qualquer lado são descartados.

    Atenção: a fórmula supõe pares INDEPENDENTES. Quando o mesmo usuário aparece em várias
    linhas, o intervalo sai estreito demais; nesse caso, o bootstrap por usuário é o mais honesto.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok], b[ok]
    n = len(a)
    r = correlacao(a, b, "pearson")
    if np.isnan(r):
        return ResultadoPearson(np.nan, np.nan, np.nan, np.nan, n)
    r = float(np.clip(r, -1.0, 1.0))

    if abs(r) == 1.0:
        p = 0.0
    else:
        t = r * math.sqrt((n - 2) / (1 - r * r))
        p = p_bicaudal_t(t, n - 2)

    if n <= 3:
        ic_inf, ic_sup = -1.0, 1.0
    else:
        z = np.arctanh(np.clip(r, -1 + 1e-15, 1 - 1e-15))
        erro = 1 / math.sqrt(n - 3)
        critico = NormalDist().inv_cdf(0.5 + confianca / 2)
        ic_inf, ic_sup = float(np.tanh(z - critico * erro)), float(np.tanh(z + critico * erro))
    return ResultadoPearson(r, p, ic_inf, ic_sup, n)
