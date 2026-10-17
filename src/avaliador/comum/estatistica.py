"""Testes t (pareado e independente) só com numpy, sem scipy.

O artigo do Dave usa scipy.stats.ttest_rel e ttest_ind. Como o scipy é bloqueado no Windows
do Victor, implementamos a distribuição t pela função beta incompleta regularizada
(Numerical Recipes, cap. 6.4). Os testes conferem os valores com o scipy quando ele existe.
"""
from __future__ import annotations

import math

import numpy as np


def _nao_zero(v: float, minimo: float = 1e-300) -> float:
    return v if abs(v) > minimo else minimo


def _beta_cf(a: float, b: float, x: float, iteracoes: int = 300, eps: float = 3e-14) -> float:
    """Fração continuada da beta incompleta (algoritmo de Lentz modificado)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 / _nao_zero(1.0 - qab * x / qap)
    h = d
    for m in range(1, iteracoes + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 / _nao_zero(1.0 + aa * d)
        c = _nao_zero(1.0 + aa / c)
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 / _nao_zero(1.0 + aa * d)
        c = _nao_zero(1.0 + aa / c)
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def beta_incompleta(a: float, b: float, x: float) -> float:
    """I_x(a, b), a função beta incompleta regularizada."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    ln = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(ln) * _beta_cf(a, b, x) / a
    return 1.0 - math.exp(ln) * _beta_cf(b, a, 1 - x) / b


def p_bicaudal_t(t: float, gl: float) -> float:
    """p-valor bicaudal de uma estatística t com `gl` graus de liberdade."""
    if not np.isfinite(t):
        return 0.0 if np.isinf(t) else np.nan
    return beta_incompleta(gl / 2, 0.5, gl / (gl + t * t))


def ttest_pareado(a, b) -> tuple[float, float]:
    """Equivalente a scipy.stats.ttest_rel(a, b, nan_policy='omit')."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    d = a[ok] - b[ok]
    n = len(d)
    if n < 2:
        return np.nan, np.nan
    dp = d.std(ddof=1)
    if dp == 0:
        return (np.nan, np.nan) if d.mean() == 0 else (np.sign(d.mean()) * np.inf, 0.0)
    t = d.mean() / (dp / math.sqrt(n))
    return float(t), p_bicaudal_t(t, n - 1)


def ttest_independente(a, b) -> tuple[float, float]:
    """Equivalente a scipy.stats.ttest_ind(a, b, nan_policy='omit') (variâncias iguais)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return np.nan, np.nan
    gl = na + nb - 2
    vp = ((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / gl
    if vp == 0:
        return np.nan, np.nan
    t = (a.mean() - b.mean()) / math.sqrt(vp * (1 / na + 1 / nb))
    return float(t), p_bicaudal_t(t, gl)


def estrelas(p: float) -> str:
    if p is None or np.isnan(p):
        return ""
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
