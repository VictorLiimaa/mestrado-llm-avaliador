"""Correlações de Pearson, Spearman e Kendall implementadas só com numpy.

O scipy faz o mesmo, mas no Windows com o "Controle Inteligente de Aplicativos" ligado as DLLs do
scipy são bloqueadas. Os testes conferem que os valores batem com o scipy quando ele está disponível.
"""
from __future__ import annotations

import warnings

import numpy as np


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
