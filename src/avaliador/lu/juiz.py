"""Usuário simulado (LLM) avaliando as explicações do Lu, com cache e combinação de modelos."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..comum import execucao
from ..comum.llm import LLM
from .dados import ASPECTOS
from .prompts import montar_prompt

# Política de Zhang et al.: resposta que não pôde ser lida vira 0, para penalizar a correlação.
NOTA_FALHA_LEITURA = 0
CAMPO_CHAVE = "row_id"


def amostrar_usuarios(df: pd.DataFrame, n_usuarios: int | None, semente: int = 2026) -> pd.DataFrame:
    """Versão reduzida: sorteia usuários inteiros, preservando os níveis usuário e par da meta-avaliação."""
    if not n_usuarios:
        return df
    usuarios = pd.Series(df["user"].unique()).sample(n=n_usuarios, random_state=semente)
    return df[df["user"].isin(usuarios)].copy()


def avaliar(
    df_completo: pd.DataFrame,
    df_alvo: pd.DataFrame,
    llm: LLM,
    condicao: str,
    arquivo_cache: str | Path,
    reproduzir_bug_transparencia: bool = False,
    resposta_curta: bool = False,
    paralelo: int = 1,
    progresso: bool = True,
) -> pd.DataFrame:
    """Avalia cada explicação de `df_alvo` e devolve o DataFrame com as notas da LLM.

    `df_completo` é usado para montar o contexto (as preferências olham os outros filmes do usuário).
    """
    registros = execucao.executar(
        itens=[linha for _, linha in df_alvo.iterrows()],
        chave=lambda linha: int(linha["row_id"]),
        montar_prompt=lambda linha: montar_prompt(
            df_completo, linha, condicao, reproduzir_bug_transparencia, resposta_curta),
        llm=llm, arquivo=arquivo_cache, campo_chave=CAMPO_CHAVE, n_notas=len(ASPECTOS),
        condicao=condicao, paralelo=paralelo, progresso=progresso,
    )
    return juntar_notas(df_alvo, registros.values(), prefixo=f"{llm.config.nome}__{condicao}")


def ler_cache(arquivo_cache: str | Path) -> list[dict]:
    return list(execucao.ler_cache(arquivo_cache, CAMPO_CHAVE).values())


def juntar_notas(df_alvo: pd.DataFrame, registros, prefixo: str) -> pd.DataFrame:
    """Acrescenta as colunas <prefixo>_<aspecto> e <prefixo>_falha ao DataFrame."""
    por_id = {r[CAMPO_CHAVE]: r["notas"] for r in registros}
    df = df_alvo.copy()
    notas = [por_id.get(int(row_id)) for row_id in df["row_id"]]
    for i, aspecto in enumerate(ASPECTOS):
        df[f"{prefixo}_{aspecto}"] = [n[i] if n else NOTA_FALHA_LEITURA for n in notas]
    df[f"{prefixo}_falha"] = [n is None for n in notas]
    return df


def combinar(df: pd.DataFrame, prefixos: list[str], nome: str) -> pd.DataFrame:
    """Combinação de vários avaliadores pela média das notas (Zhang et al., RQ3)."""
    df = df.copy()
    for aspecto in ASPECTOS:
        df[f"{nome}_{aspecto}"] = np.mean([df[f"{p}_{aspecto}"] for p in prefixos], axis=0)
    return df
