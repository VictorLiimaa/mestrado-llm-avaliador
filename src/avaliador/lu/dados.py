"""Carregamento e limpeza dos dados de Lu et al. (2023), distribuídos no repositório de Zhang et al. (2024).

Os três arquivos brutos estão alinhados linha a linha (mesma ordem de explicações):
- df_explanation.pkl: dados completos do estudo com usuários (52 colunas);
- third_party.csv: notas de dois anotadores externos (sem id de usuário);
- df_explanation_selected.csv: id numérico do usuário, usado para ligar aos dados demográficos;
- user_demo.csv: dados demográficos por usuário.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# Nomes padronizados dos quatro aspectos avaliados pelos usuários.
ASPECTOS = ["persuasiveness", "transparency", "accuracy", "satisfaction"]

# Nome de cada aspecto em cada arquivo bruto.
_COLUNAS_USUARIO = {
    "persuasiveness": "persuasiveness",
    "transparency": "transparency",
    "accuracy": "interest_accuracy",
    "satisfaction": "satisfaction",
}
_COLUNAS_ANOTADOR = {
    "persuasiveness": "persuasiveness",
    "transparency": "transparency",
    "accuracy": "accuracy",
    "satisfaction": "satisfactory",
}

# Política de Zhang et al.: nota de usuário ausente vira 3 (atitude desconhecida).
NOTA_USUARIO_AUSENTE = 3


def carregar(pasta: str | Path) -> pd.DataFrame:
    """Devolve uma linha por explicação, com notas reais, notas dos anotadores e contexto do usuário."""
    pasta = Path(pasta)
    if not (pasta / "df_explanation.pkl").exists():
        raise FileNotFoundError(f"Dados do Lu não encontrados em {pasta}. "
                                "Rode antes: python scripts/dados_baixar_lu.py")
    completo = pd.read_pickle(pasta / "df_explanation.pkl")
    anotadores = pd.read_csv(pasta / "third_party.csv")
    selecionado = pd.read_csv(pasta / "df_explanation_selected.csv")
    demografia = pd.read_csv(pasta / "user_demo.csv")

    if not (len(completo) == len(anotadores) == len(selecionado)):
        raise ValueError("Os arquivos brutos não têm o mesmo número de linhas.")
    for col in ("movie_id", "explanation_type"):
        if not (completo[col].values == anotadores[col].values).all():
            raise ValueError(f"Arquivos desalinhados na coluna {col}.")

    df = pd.DataFrame(
        {
            "user": completo["user_id"].values,
            "rouge1_lu": completo["rouge-1"].values,
            "rougel_lu": completo["rouge-L"].values,
            "user_num": selecionado["user_id"].values,
            "movie_id": completo["movie_id"].values,
            "movie_title": completo["movie_title"].values,
            "explanation_type": completo["explanation_type"].values,
            "self_explanation": completo["self_explanation"].values,
            "self_attributes": completo["self_attributes"].values,
            "self_summary": completo["peer_summary_ans"]
            .apply(lambda d: d.get("self_summary") if isinstance(d, dict) else None)
            .values,
        }
    )
    # Texto limpo da explicação: usamos a versão já limpa por Zhang et al. (third_party.csv),
    # porque o HTML original tem tags dentro de atributos que confundem uma limpeza por regex.
    df["explanation"] = anotadores["explanation_text"].astype(str).values

    for aspecto in ASPECTOS:
        df[f"user_{aspecto}"] = (
            completo[_COLUNAS_USUARIO[aspecto]].astype(float).fillna(NOTA_USUARIO_AUSENTE).values
        )
        coluna = _COLUNAS_ANOTADOR[aspecto]
        df[f"anot1_{aspecto}"] = anotadores[f"{coluna}_1"].astype(float).values
        df[f"anot2_{aspecto}"] = anotadores[f"{coluna}_2"].astype(float).values
        df[f"anotmedia_{aspecto}"] = (df[f"anot1_{aspecto}"] + df[f"anot2_{aspecto}"]) / 2

    demografia = demografia.rename(columns={"user_id": "user_num"})
    df = df.merge(demografia, on="user_num", how="left")
    df.insert(0, "row_id", range(len(df)))
    return df
