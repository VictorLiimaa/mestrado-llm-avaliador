"""Baseline do baseline: métricas baseadas em referência (BLEU, ROUGE).

Seguindo Zhang et al. (2024), a referência é a explicação que o próprio usuário escreveu
(self_explanation). Os textos estão em chinês, então a tokenização é por caractere.

Reprodutibilidade:
- ROUGE: usamos os valores pré-calculados que vêm nos dados de Lu et al. (colunas rouge-1 e
  rouge-L). Eles ficam a menos de 0,5 ponto percentual da Tabela 1 de Zhang et al. no nível
  do conjunto. Também deixamos uma implementação própria (rouge_1_f, rouge_l_f) para textos novos.
- BLEU: o código de BLEU de Zhang et al. não foi publicado, então a configuração exata
  (tokenização, suavização) é desconhecida. Usamos tokens por caractere, BLEU-1 sem suavização
  e BLEU-4 com a suavização method1 do NLTK. Os números ficam próximos, mas não idênticos.
"""
from __future__ import annotations

import warnings
from collections import Counter

import pandas as pd
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

from .dados import ASPECTOS

_SUAVIZACAO = SmoothingFunction().method1


def tokenizar(texto) -> list[str]:
    """Tokens por caractere, ignorando espaços."""
    return [c for c in str(texto) if not c.isspace()] if isinstance(texto, str) else []


def bleu(candidato: list[str], referencia: list[str], n: int) -> float:
    if not candidato or not referencia:
        return 0.0
    pesos = tuple([1.0 / n] * n)
    suavizacao = None if n == 1 else _SUAVIZACAO
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return float(sentence_bleu([referencia], candidato, weights=pesos, smoothing_function=suavizacao))


def _f1(precisao: float, revocacao: float) -> float:
    return 0.0 if precisao + revocacao == 0 else 2 * precisao * revocacao / (precisao + revocacao)


def rouge_1_f(candidato: list[str], referencia: list[str]) -> float:
    if not candidato or not referencia:
        return 0.0
    sobreposicao = sum((Counter(candidato) & Counter(referencia)).values())
    return _f1(sobreposicao / len(candidato), sobreposicao / len(referencia))


def _lcs(a: list[str], b: list[str]) -> int:
    anterior = [0] * (len(b) + 1)
    for x in a:
        atual = [0]
        for j, y in enumerate(b, start=1):
            atual.append(anterior[j - 1] + 1 if x == y else max(anterior[j], atual[j - 1]))
        anterior = atual
    return anterior[-1]


def rouge_l_f(candidato: list[str], referencia: list[str]) -> float:
    if not candidato or not referencia:
        return 0.0
    lcs = _lcs(candidato, referencia)
    return _f1(lcs / len(candidato), lcs / len(referencia))


def media_do_tipo(df: pd.DataFrame) -> pd.DataFrame:
    """Baseline ingênuo: a nota prevista é a média que OS OUTROS usuários deram a esse tipo de explicação.

    Não lê o texto nem conhece o usuário: só sabe que, em geral, explicações do tipo "peer" agradam
    mais que as do tipo "attr_random". O próprio usuário fica de fora da média (deixa-um-usuário-de-fora),
    para que a nota real dele não vaze para a previsão. Serve para responder: o juiz LLM faz algo além
    de reconhecer qual TIPO de explicação costuma ser melhor?
    """
    df = df.copy()
    for aspecto in ASPECTOS:
        coluna = f"user_{aspecto}"
        soma_tipo = df.groupby("explanation_type")[coluna].transform("sum")
        n_tipo = df.groupby("explanation_type")[coluna].transform("count")
        soma_usuario = df.groupby(["explanation_type", "user"])[coluna].transform("sum")
        n_usuario = df.groupby(["explanation_type", "user"])[coluna].transform("count")
        df[f"tipo_{aspecto}"] = (soma_tipo - soma_usuario) / (n_tipo - n_usuario)
    return df


def calcular_metricas_referencia(df: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta colunas <metrica>_<aspecto>. A mesma nota vale para os 4 aspectos, como no artigo."""
    df = df.copy()
    candidatos = df["explanation"].apply(tokenizar)
    referencias = df["self_explanation"].apply(tokenizar)
    valores = {
        "bleu1": [bleu(c, r, 1) for c, r in zip(candidatos, referencias)],
        "bleu4": [bleu(c, r, 4) for c, r in zip(candidatos, referencias)],
        "rouge1f": df["rouge1_lu"].astype(float).tolist(),
        "rougelf": df["rougel_lu"].astype(float).tolist(),
    }
    for nome, lista in valores.items():
        for aspecto in ASPECTOS:
            df[f"{nome}_{aspecto}"] = lista
    return df
