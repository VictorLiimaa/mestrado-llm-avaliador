"""Prompt do ouvinte simulado para o teste do Dave.

A LLM vê o mesmo que o participante via na tela: a primeira música, o segue e a segunda música,
e responde às mesmas 8 afirmações, na mesma ordem e com a mesma escala de 1 a 5.
A introdução resume o texto de boas-vindas do teste original (templates/user_trial_page_intro.html).

Condições:
- E0: nenhuma informação sobre o ouvinte (como o E0 do experimento com o Lu).
Condições com informação sobre UM participante (teste de treino e teste, `montar_prompt_ouvinte`):
- historico: as notas que ele deu aos segues dos outros pares;
- perfil: as respostas dele sobre si (engajamento musical, shows, tempo de escuta, inglês);
- familiaridade: se ele conhecia as músicas e os artistas do segue;
- combinações (ver avaliador.dave.treino_teste.CONDICOES_OUVINTE).
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


def _fim(resposta_curta: bool) -> str:
    return (
        "Answer with ONLY the eight integers separated by spaces, in the order above, and nothing "
        "else. Example: 3 3 3 3 3 3 3 3"
        if resposta_curta
        else "Think briefly about the segue, then end your answer with the eight integers separated "
        "by spaces, in the order above. Example: 3 3 3 3 3 3 3 3"
    )


def _afirmacoes() -> str:
    return "\n".join(f"{i + 1}. {FRASES[m]}" for i, m in enumerate(METRICAS))


def _segue(segue: pd.Series) -> str:
    return (f"First track: {segue['musica1']} by {segue['artista1']}\n"
            f"Segue: {segue['texto']}\n"
            f"Second track: {segue['musica2']} by {segue['artista2']}")


_ESCALA = ("Rate how much you agree with each statement, with an integer from 1 to 5 "
           "(1 = strongly disagree, 2 = disagree, 3 = neutral, 4 = agree, 5 = strongly agree):\n")


def montar_prompt(segue: pd.Series, condicao: str = "E0", resposta_curta: bool = True) -> str:
    if condicao not in CONDICOES:
        raise ValueError(f"Condição desconhecida: {condicao}. Opções: {CONDICOES}")
    return f"{_INTRO}\n\n{_segue(segue)}\n\n{_ESCALA}{_afirmacoes()}\n\n{_fim(resposta_curta)}"


def _formatar_notas(notas) -> str:
    return " ".join("-" if v is None or v != v else str(int(v)) for v in notas)


def _familiaridade(segue: pd.Series, fam: dict | None) -> str:
    """Uma linha dizendo o que o participante conhecia neste segue (como respondeu no teste)."""
    if not fam:
        return ""
    def sim_nao(v):
        return "yes" if v is True else "no" if v is False else "not answered"
    return (f"Before the survey you said whether you know these songs and artists: "
            f"first song {sim_nao(fam.get('conhece_musica1'))}, first artist "
            f"{sim_nao(fam.get('conhece_artista1'))}, second song {sim_nao(fam.get('conhece_musica2'))}, "
            f"second artist {sim_nao(fam.get('conhece_artista2'))}.")


def montar_prompt_ouvinte(segue: pd.Series, perfil: list | None = None, familiaridade: dict | None = None,
                          treino: list | None = None, resposta_curta: bool = True) -> str:
    """Prompt do ouvinte simulado com informação sobre UM participante (teste de treino e teste).

    - perfil: pares (pergunta, resposta) que o participante deu sobre si no início do teste
      (engajamento musical do Gold-MSI, shows, tempo de escuta, nível de inglês);
    - familiaridade: se ele conhecia as músicas e os artistas do segue (dict com conhece_*);
      também aparece em cada exemplo do treino, quando há treino;
    - treino: lista de (segue, notas[, familiaridade]) com as notas que ELE deu aos segues dos
      outros pares. O par do teste nunca aparece no treino.
    Sem nenhum dos três, use `montar_prompt` (E0).
    """
    partes = [_INTRO]
    if perfil:
        partes.append("About you (your own answers at the start of the survey):\n" +
                      "\n".join(f'- "{pergunta}": {resposta}' if pergunta.endswith(".")
                                 else f"- {pergunta}: {resposta}" for pergunta, resposta in perfil))
    partes.append("In this survey you rate each segue on these eight statements, from 1 to 5 "
                  "(1 = strongly disagree, 2 = disagree, 3 = neutral, 4 = agree, 5 = strongly agree):\n"
                  + _afirmacoes())
    if treino:
        exemplos = []
        for i, item in enumerate(treino):
            s, notas = item[0], item[1]
            fam = item[2] if len(item) > 2 and familiaridade is not None else None
            linhas = [f"Segue {i + 1}", _segue(s)]
            if fam:
                linhas.append(_familiaridade(s, fam))
            linhas.append(f"Your ratings: {_formatar_notas(notas)}")
            exemplos.append("\n".join(linhas))
        partes.append("Here are the segues you have already rated, with your own ratings in the order above:\n\n"
                      + "\n\n".join(exemplos))
        partes.append("Now rate this new segue the way you would, consistently with your previous answers:")
    else:
        partes.append("Now rate this segue the way you would:")
    bloco = _segue(segue)
    if familiaridade is not None:
        bloco += "\n" + _familiaridade(segue, familiaridade)
    partes.append(bloco)
    partes.append(_fim(resposta_curta))
    return "\n\n".join(partes)


def montar_prompt_historico(segue: pd.Series, treino: list, resposta_curta: bool = True) -> str:
    """Condição `historico`: só as notas que o participante deu aos outros pares."""
    return montar_prompt_ouvinte(segue, treino=treino, resposta_curta=resposta_curta)


def _sim_nao(v) -> str:
    return "yes" if v is True else "no" if v is False else "not answered"


FORMATO_PAR = "1:? 2:? 3:? 4:? 5:? 6:? 7:? 8:?"


def montar_prompt_par(segue_a: pd.Series, segue_b: pd.Series, perfil: list | None = None,
                      fam_a: dict | None = None, fam_b: dict | None = None, treino: list | None = None) -> str:
    """Comparação direta: os dois segues de um par (mesma primeira música) lado a lado.

    Para cada afirmação, a LLM diz qual dos dois segues ela descreve melhor PARA ESTA PESSOA (A ou
    B). Comparando dentro do par, o "jeito" da pessoa (dar notas altas ou baixas) não entra: só a
    reação ao conteúdo. A ordem A/B é decidida por quem chama (cada par é perguntado nas duas).
    perfil, familiaridade (fam_a, fam_b) e treino têm o mesmo formato de `montar_prompt_ouvinte`.
    """
    partes = [_INTRO]
    if perfil:
        partes.append("About you (your own answers at the start of the survey):\n" +
                      "\n".join(f'- "{pergunta}": {resposta}' if pergunta.endswith(".")
                                else f"- {pergunta}: {resposta}" for pergunta, resposta in perfil))
    partes.append("In this survey segues are judged on these eight statements:\n" + _afirmacoes())
    if treino:
        exemplos = []
        for i, item in enumerate(treino):
            s, notas = item[0], item[1]
            exemplos.append(f"Segue {i + 1}\n{_segue(s)}\nYour ratings (1 = strongly disagree, "
                            f"5 = strongly agree): {_formatar_notas(notas)}")
        partes.append("Here are other segues you have already rated, with your own ratings in the "
                      "order above:\n\n" + "\n\n".join(exemplos))
    blocos = [f"First track (the same for both): {segue_a['musica1']} by {segue_a['artista1']}"]
    for letra, s, fam in [("A", segue_a, fam_a), ("B", segue_b, fam_b)]:
        linha = f"Segue {letra}: {s['texto']}\nSecond track {letra}: {s['musica2']} by {s['artista2']}"
        if fam:
            linha += f"\nYou know second track {letra}: {_sim_nao(fam.get('conhece_musica2'))}; " \
                     f"its artist: {_sim_nao(fam.get('conhece_artista2'))}."
        blocos.append(linha)
    if fam_a:
        blocos.append(f"You know the first track: {_sim_nao(fam_a.get('conhece_musica1'))}; "
                      f"its artist: {_sim_nao(fam_a.get('conhece_artista1'))}.")
    partes.append("Now compare these two segues, which start from the same first song:\n\n" + "\n\n".join(blocos))
    # Sem exemplo de resposta: na primeira versão o Qwen copiou o exemplo ("A B B A A B A B") em
    # 83-92% dos pares. Aqui o formato tem só lacunas (?), sem nenhuma escolha pronta.
    partes.append("For each of the eight statements, which segue does it describe better for you, A or B? "
                  "Reply in exactly this format, replacing each ? with A or B, and write nothing else:\n"
                  + FORMATO_PAR)
    return "\n\n".join(partes)
