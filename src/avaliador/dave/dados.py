"""Leitura dos dados do teste com usuários do Dave.

Duas tabelas:
- `segues`: uma linha por segue avaliado (par x sistema), com as músicas, o texto e a categoria.
  É o que a LLM recebe: 172 pares x 2 sistemas.
- `notas`: uma linha por (participante, segue), com as 8 notas de 1 a 5. É o "gabarito" humano.

Filtros iguais aos do artigo (analyze_answers.load_answers): descarta respostas com menos de
3 minutos e participantes com inglês "Mid". Sobram 151 participantes.

Atenção: o nome do arquivo em user_trial_sample/ (ex.: 1927.json) é o identificador usado nas
respostas. O campo "idx" dentro do arquivo é outro número e não deve ser usado.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

# Ordem das perguntas na tela do teste (q_0 ... q_7), conforme analyze_answers.segue_eval_df.
METRICAS = [
    "likeable", "high_quality", "understandable", "sparked_interest",
    "funny", "informative", "creative", "well_written",
]
# Frases exatas mostradas aos participantes (templates/user_trial_page_segue_eval.html).
FRASES = {
    "likeable": "I like this segue",
    "high_quality": "This is a high quality segue",
    "understandable": "I understand the connection between the two songs",
    "sparked_interest": "This segue sparked my interest in the second song",
    "funny": "This segue is funny",
    "informative": "This segue is informative",
    "creative": "This segue is creative",
    "well_written": "This segue is well written",
}
LIKERT = {"Strongly disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly agree": 5}
SISTEMAS = ["dave", "the_chain"]


def carregar_respostas(pasta: str | Path) -> list[dict]:
    respostas = json.loads((Path(pasta) / "answers.json").read_text(encoding="utf-8"))
    return [
        r for r in respostas
        if r["elapsed_time"] / 60 >= 3 and r.get("proficiency_q_0") != "Mid"
    ]


def carregar_segues(pasta: str | Path) -> pd.DataFrame:
    """Uma linha por (segue_idx, sistema): músicas, texto do segue e categoria F/I."""
    pasta = Path(pasta)
    categorias = {}
    for sistema in SISTEMAS:
        csv = pd.read_csv(pasta / f"df_segue_category_{sistema}.csv")
        for _, linha in csv.iterrows():
            categorias[(int(linha["segue_idx"]), sistema)] = linha["category (F/I)"]

    linhas = []
    for arquivo in sorted((pasta / "user_trial_sample").glob("*.json")):
        d = json.loads(arquivo.read_text(encoding="utf-8"))
        segue_idx = int(arquivo.stem)
        semente = d["seed_song"]
        textos = {"dave": d["segue_dave"]["line"], "the_chain": d["segue_the_chain"]}
        for sistema in SISTEMAS:
            segunda = d[f"song_{sistema}"]
            linhas.append({
                "segue_idx": segue_idx,
                "sistema": sistema,
                "musica1": semente["track_name"],
                "artista1": semente["artist_name"],
                "musica2": segunda["track_name"],
                "artista2": segunda["artist_name"],
                "texto": textos[sistema],
                "categoria": categorias.get((segue_idx, sistema)),
                "interestingness": float(d["segue_dave"]["score"]) if sistema == "dave" else None,
            })
    return pd.DataFrame(linhas)


def carregar_notas(pasta: str | Path) -> pd.DataFrame:
    """Uma linha por (participante, segue avaliado), com as 8 notas humanas."""
    linhas = []
    for usuario, resposta in enumerate(carregar_respostas(pasta)):
        for chave in resposta:
            m = re.match(r"segue_eval_(\d)_(\d+)_(dave|the_chain)_q_0$", chave)
            if not m:
                continue
            posicao, segue_idx, sistema = m.groups()
            linha = {"usuario": usuario, "segue_idx": int(segue_idx), "sistema": sistema,
                     "posicao": int(posicao)}
            for i, metrica in enumerate(METRICAS):
                valor = resposta.get(f"segue_eval_{posicao}_{segue_idx}_{sistema}_q_{i}")
                linha[metrica] = LIKERT.get(valor)
            linhas.append(linha)
    return pd.DataFrame(linhas)


def carregar(pasta: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (segues, notas), só com os segues que foram de fato avaliados."""
    if not (Path(pasta) / "answers.json").exists():
        raise FileNotFoundError(f"Dados do Dave não encontrados em {pasta}. Rode antes: "
                                "python scripts/dados_preparar_dave.py <zip do Zenodo>")
    segues = carregar_segues(pasta)
    notas = carregar_notas(pasta)
    notas = notas.merge(segues[["segue_idx", "sistema", "categoria"]], on=["segue_idx", "sistema"],
                        how="left")
    avaliados = notas[["segue_idx", "sistema"]].drop_duplicates()
    segues = segues.merge(avaliados, on=["segue_idx", "sistema"]).reset_index(drop=True)
    return segues, notas
