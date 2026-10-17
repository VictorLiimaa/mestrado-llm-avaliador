"""Ouvinte simulado (LLM) avaliando cada segue do teste do Dave, com cache."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..comum import execucao
from ..comum.llm import LLM
from .dados import METRICAS
from .prompts import montar_prompt

CAMPO_CHAVE = "chave"


def chave(segue_idx, sistema) -> str:
    return f"{int(segue_idx)}_{sistema}"


def avaliar(segues: pd.DataFrame, llm: LLM, condicao: str, arquivo_cache: str | Path,
            resposta_curta: bool = True, paralelo: int = 1, progresso: bool = True) -> dict:
    return execucao.executar(
        itens=[s for _, s in segues.iterrows()],
        chave=lambda s: chave(s["segue_idx"], s["sistema"]),
        montar_prompt=lambda s: montar_prompt(s, condicao, resposta_curta),
        llm=llm, arquivo=arquivo_cache, campo_chave=CAMPO_CHAVE, n_notas=len(METRICAS),
        condicao=condicao, paralelo=paralelo, progresso=progresso,
    )


def ler_cache(arquivo_cache: str | Path) -> dict:
    return execucao.ler_cache(arquivo_cache, CAMPO_CHAVE)


def tabela_notas(segues: pd.DataFrame, registros: dict) -> pd.DataFrame:
    """Uma linha por segue com as 8 notas da LLM (NaN se a resposta não pôde ser lida)."""
    linhas = []
    for _, s in segues.iterrows():
        r = registros.get(chave(s["segue_idx"], s["sistema"]))
        notas = r["notas"] if r else None
        linha = {"segue_idx": s["segue_idx"], "sistema": s["sistema"], "falha": notas is None}
        for i, m in enumerate(METRICAS):
            linha[m] = notas[i] if notas else float("nan")
        linhas.append(linha)
    return pd.DataFrame(linhas)
