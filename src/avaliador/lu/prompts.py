"""Prompts do usuário simulado / juiz LLM, com níveis de enriquecimento.

Ponto de partida: o prompt multi-aspecto de Zhang et al. (2024). Duas diferenças deliberadas:
1. Correção de um erro do código original: lá, a linha "Transparency" recebia a descrição de
   persuasão. Aqui cada aspecto recebe a própria descrição. Para reproduzir o original fielmente,
   use `reproduzir_bug_transparencia=True`.
2. Níveis de enriquecimento (contexto do usuário), cumulativos:
   - E0: título do filme + explicação (zero-shot de Zhang et al.).
   - E1: + dados demográficos do usuário.
   - E2: + resumo do gosto escrito pelo próprio usuário.
   - E3: + preferências gerais por atributos, agregadas dos OUTROS filmes do usuário.

Regras contra vazamento de resposta (nunca entram no prompt):
- self_explanation e evaluate_reason: escritos pelo usuário depois de ver as explicações;
- preferências por atributo marcadas no próprio filme avaliado (por isso E3 usa só outros filmes);
- pre_knowledge: varia entre explicações do mesmo par usuário-filme, então pode ter sido coletado
  depois da explicação. Fica de fora até isso ser confirmado no artigo de Lu et al.
"""
from __future__ import annotations

import html
from collections import Counter

import pandas as pd

from .dados import ASPECTOS

DESCRICOES = {
    "persuasiveness": "This explanation is convincing to me.",
    "transparency": "Based on this explanation, I understand why this movie is recommended.",
    "accuracy": "This explanation is consistent with my interests.",
    "satisfaction": "I am satisfied with this explanation.",
}
ROTULOS = {
    "persuasiveness": "Persuasiveness",
    "transparency": "Transparency",
    "accuracy": "Accuracy",
    "satisfaction": "Satisfactory",
}

# Cada condição lista os blocos de contexto que entram no prompt.
# E1-E3 são cumulativos (como na primeira rodada); os "so_*" isolam um contexto por vez,
# para medir o efeito de cada um separadamente.
CONDICOES = {
    "E0": [],
    "E1": ["demografia"],
    "E2": ["demografia", "resumo"],
    "E3": ["demografia", "resumo", "preferencias"],
    "so_demografia": ["demografia"],
    "so_resumo": ["resumo"],
    "so_preferencias": ["preferencias"],
    "resumo_preferencias": ["resumo", "preferencias"],
    # "foco_*": mesmo contexto, mas com uma instrução que manda julgar SÓ a explicação,
    # não se o usuário gostaria do filme. foco_E0 é o controle (instrução sem perfil),
    # para separar o efeito da instrução do efeito do perfil.
    "foco_E0": [],
    "foco_demografia": ["demografia"],
    "foco_resumo": ["resumo"],
    "foco_preferencias": ["preferencias"],
}
NIVEIS_ENRIQUECIMENTO = list(CONDICOES)

_INSTRUCAO_LIKERT = (
    "Try to immerse yourself in this user's experience and provide feedback. "
    "Consider how the user would feel about the explanation if he/she were recommended the movie."
)


def _demografia(linha: pd.Series) -> str:
    if pd.isna(linha.get("gender")):
        return ""
    campo = lambda nome: html.unescape(str(linha[nome]))  # noqa: E731 (os dados têm "&lt;100")
    return (
        f"Your gender is: {campo('gender')}. "
        f"Your interest in movies is: {campo('user_movie_interest')}. "
        f"Number of movies you watch per year: {campo('peryear')}. "
        f"Total number of movies you have watched: around {campo('total')}."
    )


def _resumo_gosto(linha: pd.Series) -> str:
    resumo = linha.get("self_summary")
    if not isinstance(resumo, str) or not resumo.strip():
        return ""
    return f"In your own words, your taste in movies is: {resumo.strip()}"


def preferencias_gerais(df: pd.DataFrame, usuario, filme, top: int = 8) -> tuple[list[str], list[str]]:
    """Atributos que o usuário marcou como positivos/negativos nos OUTROS filmes (deixa o filme atual de fora).

    Cada atributo bruto tem o formato 'tipo=valor=polaridade', por exemplo '类型=历史=neg'.
    Contamos uma vez por filme (as linhas do mesmo filme repetem a lista).
    """
    outros = df[(df["user"] == usuario) & (df["movie_id"] != filme)].drop_duplicates("movie_id")
    positivos, negativos = Counter(), Counter()
    for atributos in outros["self_attributes"]:
        if not isinstance(atributos, (list, tuple)):
            continue
        for item in atributos:
            partes = str(item).split("=")
            if len(partes) != 3:
                continue
            tipo, valor, polaridade = partes
            # Atributos sem valor próprio (ex.: "o meu amigo também gostou=1") viram só o tipo.
            rotulo = tipo if valor == "1" else f"{tipo}: {valor}"
            if polaridade == "pos":
                positivos[rotulo] += 1
            elif polaridade == "neg":
                negativos[rotulo] += 1
    return [a for a, _ in positivos.most_common(top)], [a for a, _ in negativos.most_common(top)]


def _preferencias(df: pd.DataFrame, linha: pd.Series) -> str:
    positivos, negativos = preferencias_gerais(df, linha["user"], linha["movie_id"])
    partes = []
    if positivos:
        partes.append("In other movies, you liked these aspects: " + "; ".join(positivos) + ".")
    if negativos:
        partes.append("In other movies, you disliked these aspects: " + "; ".join(negativos) + ".")
    return " ".join(partes)


def contexto_usuario(df: pd.DataFrame, linha: pd.Series, nivel: str) -> str:
    if nivel not in CONDICOES:
        raise ValueError(f"Condição de enriquecimento desconhecida: {nivel}. Opções: {list(CONDICOES)}")
    geradores = {
        "demografia": lambda: _demografia(linha),
        "resumo": lambda: _resumo_gosto(linha),
        "preferencias": lambda: _preferencias(df, linha),
    }
    blocos = [geradores[b]() for b in CONDICOES[nivel]]
    blocos = [b for b in blocos if b]
    return "" if not blocos else "You are a user with the following profile:\n" + "\n".join(blocos)


_INSTRUCAO_FOCO = (
    "Important: judge only the quality of the explanation text itself, as this user would perceive it. "
    "Do not rate whether this user would like the movie, and do not assume the user is more or less "
    "demanding because of the profile. Use the profile only to understand what the user cares about."
)


def montar_prompt(
    df: pd.DataFrame,
    linha: pd.Series,
    nivel: str = "E0",
    reproduzir_bug_transparencia: bool = False,
    resposta_curta: bool = False,
) -> str:
    """Prompt multi-aspecto: a LLM devolve quatro notas de 1 a 5.

    Com `resposta_curta=True`, pede só os quatro números. A geração fica muito mais rápida,
    mas o modelo deixa de "pensar em voz alta" antes de dar as notas, o que pode mudar os
    resultados: compare com uma amostra antes de trocar a configuração principal.
    """
    descricoes = dict(DESCRICOES)
    if reproduzir_bug_transparencia:
        descricoes["transparency"] = DESCRICOES["persuasiveness"]
    aspectos = "\n".join(f"{ROTULOS[a]}: {descricoes[a]}" for a in ASPECTOS)
    contexto = contexto_usuario(df, linha, nivel)
    return (
        "Considering you are a user of a movie recommendation platform.\n"
        + (contexto + "\n\n" if contexto else "\n")
        + f"The recommendation system has suggested the movie '{linha['movie_title']}' to you, "
        f"accompanied by the following explanation text:\n\n'{linha['explanation']}'\n\n"
        f"{_INSTRUCAO_LIKERT}\n\n"
        + (_INSTRUCAO_FOCO + "\n\n" if nivel.startswith("foco_") else "")
        + "Please rate the explanation on the following aspects, with integers between 1 and 5, "
        "where 1 means strongly disagree and 5 means strongly agree:\n"
        f"{aspectos}\n\n"
        + (
            "Answer with ONLY the four integers separated by spaces, in the order above, "
            "and nothing else. Example: 3 3 3 3"
            if resposta_curta
            else "Provide your ratings as four numbers separated by spaces, in the order above. "
            "End your answer with the four scores, for example: 3 3 3 3"
        )
    )
