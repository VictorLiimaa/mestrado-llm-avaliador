"""Prompt do ouvinte simulado para o teste do Dave.

A LLM vê o mesmo que o participante via na tela: a primeira música, o segue e a segunda música,
e responde às mesmas 8 afirmações, na mesma ordem e com a mesma escala de 1 a 5.
A introdução resume o texto de boas-vindas do teste original (templates/user_trial_page_intro.html).

Condições:
- E0: nenhuma informação sobre o ouvinte (como o E0 do experimento com o Lu).
Condições com perfil do ouvinte (engajamento musical, familiaridade) entram na etapa de
enriquecimento, depois de validado o E0.
"""
from __future__ import annotations

import pandas as pd

from .dados import FRASES, METRICAS

_INTRO = (
    "You are taking part in a music survey. A segue is a short piece of text that connects "
    "two songs played one after the other, for example by a word that appears in both titles, "
    "or by a person who worked on both tracks. You don't need to know the songs: the survey is "
    "about the segue, not about the songs."
)

CONDICOES = ["E0"]


def montar_prompt(segue: pd.Series, condicao: str = "E0", resposta_curta: bool = True) -> str:
    if condicao not in CONDICOES:
        raise ValueError(f"Condição desconhecida: {condicao}. Opções: {CONDICOES}")
    afirmacoes = "\n".join(f"{i + 1}. {FRASES[m]}" for i, m in enumerate(METRICAS))
    fim = (
        "Answer with ONLY the eight integers separated by spaces, in the order above, and nothing "
        "else. Example: 3 3 3 3 3 3 3 3"
        if resposta_curta
        else "Think briefly about the segue, then end your answer with the eight integers separated "
        "by spaces, in the order above. Example: 3 3 3 3 3 3 3 3"
    )
    return (
        f"{_INTRO}\n\n"
        f"First track: {segue['musica1']} by {segue['artista1']}\n"
        f"Segue: {segue['texto']}\n"
        f"Second track: {segue['musica2']} by {segue['artista2']}\n\n"
        "Rate how much you agree with each statement, with an integer from 1 to 5 "
        "(1 = strongly disagree, 2 = disagree, 3 = neutral, 4 = agree, 5 = strongly agree):\n"
        f"{afirmacoes}\n\n{fim}"
    )
