"""Comparação direta no par: separar o "jeito" da pessoa do julgamento do conteúdo.

No teste de treino e teste (notas de 1 a 5, um segue por vez), a LLM com histórico aprendeu a
copiar o nível de notas da pessoa e deixou de ler o segue. Aqui ela não dá notas: vê os DOIS
segues de um par lado a lado (mesma primeira música; um do Dave e um da The Chain) e diz, para
cada afirmação, qual dos dois a descreve melhor para aquela pessoa (A ou B). O nível de notas da
pessoa não tem como entrar; só a preferência.

Viés de posição: modelos pequenos tendem a escolher sempre A (ou B). Por isso cada par é
perguntado nas duas ordens (Dave como A e Dave como B). Por métrica, a preferência prevista é a
média das duas respostas, codificada como +1 (Dave) e −1 (The Chain): +1 ou −1 quando as duas
ordens concordam, 0 quando se contradizem (a escolha dependia só da posição).

Condições (o que o prompt sabe sobre a pessoa): E0 (nada; uma pergunta por par, vale para todos
que o viram), perfil, familiaridade, historico (as notas dela nos outros pares) e completo.
A avaliação usa `escolha_par.comparar`, a mesma da escolha derivada das notas separadas.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from ..comum import execucao
from ..comum.llm import LLM, ler_escolhas
from .dados import METRICAS
from .prompts import montar_prompt_par
from .treino_teste import FAMILIARIDADE, treino_de

CAMPO_CHAVE = "chave"
ORDENS = ["dave_primeiro", "chain_primeiro"]
# (histórico, perfil, familiaridade)
CONDICOES_PAR = {
    "E0": (False, False, False),
    "perfil": (False, True, False),
    "familiaridade": (False, False, True),
    "historico": (True, False, False),
    "completo": (True, True, True),
}


def chave(usuario, segue_idx, ordem) -> str:
    return f"{int(segue_idx)}_{ordem}" if usuario is None else f"{int(usuario)}_{int(segue_idx)}_{ordem}"


def itens(notas: pd.DataFrame, segues: pd.DataFrame, condicao: str, perfis: dict | None = None,
          familiaridade: pd.DataFrame | None = None) -> list[dict]:
    """Um item por (participante, par, ordem); no E0, um por (par, ordem)."""
    if condicao not in CONDICOES_PAR:
        raise ValueError(f"Condição desconhecida: {condicao}. Opções: {list(CONDICOES_PAR)}")
    com_historico, com_perfil, com_fam = CONDICOES_PAR[condicao]
    if (com_perfil and perfis is None) or (com_fam and familiaridade is None):
        raise ValueError(f"A condição {condicao} precisa de perfis e familiaridade.")
    por_segue = segues.set_index(["segue_idx", "sistema"])
    fam = familiaridade.set_index(["usuario", "posicao"])[FAMILIARIDADE].to_dict("index") if com_fam else {}

    saida = []
    if condicao == "E0":
        pares = [(None, idx, {}) for idx in sorted(notas["segue_idx"].unique())]
    else:
        pares = []
        for (u, idx), g in notas.groupby(["usuario", "segue_idx"]):
            posicoes = dict(zip(g["sistema"], g["posicao"]))
            if set(posicoes) == {"dave", "the_chain"}:
                pares.append((int(u), int(idx), posicoes))
    for u, idx, posicoes in pares:
        dave, chain = por_segue.loc[(idx, "dave")], por_segue.loc[(idx, "the_chain")]
        fam_dave = fam.get((u, int(posicoes["dave"]))) if com_fam else None
        fam_chain = fam.get((u, int(posicoes["the_chain"]))) if com_fam else None
        treino = None
        if com_historico:
            treino = [(por_segue.loc[(t["segue_idx"], t["sistema"])], [t[m] for m in METRICAS])
                      for _, t in treino_de(notas, u, idx).iterrows()]
        for ordem in ORDENS:
            a, b, fa, fb = (dave, chain, fam_dave, fam_chain) if ordem == "dave_primeiro" else \
                           (chain, dave, fam_chain, fam_dave)
            saida.append({
                "usuario": u, "segue_idx": int(idx), "ordem": ordem,
                "prompt": montar_prompt_par(a, b, perfil=perfis.get(u) if com_perfil else None,
                                            fam_a=fa, fam_b=fb, treino=treino),
            })
    return saida


def avaliar(notas: pd.DataFrame, segues: pd.DataFrame, llm: LLM, arquivo_cache: str | Path,
            condicao: str, perfis: dict | None = None, familiaridade: pd.DataFrame | None = None,
            paralelo: int = 1, progresso: bool = True) -> dict:
    return execucao.executar(
        itens=itens(notas, segues, condicao, perfis, familiaridade),
        chave=lambda i: chave(i["usuario"], i["segue_idx"], i["ordem"]),
        montar_prompt=lambda i: i["prompt"],
        llm=llm, arquivo=arquivo_cache, campo_chave=CAMPO_CHAVE, n_notas=len(METRICAS),
        condicao=f"par_{condicao}", paralelo=paralelo, progresso=progresso, ler=ler_escolhas,
    )


def ler_cache(arquivo_cache: str | Path) -> dict:
    return execucao.ler_cache(arquivo_cache, CAMPO_CHAVE)


_NUMERADA_COM_VAZIO = re.compile(r"(\d+)\s*:\s*([AB?])(?![A-Za-z])")


def ler_escolhas_com_vazio(resposta) -> list[int] | None:
    """Lê o formato "1:A 2:? ..." aceitando "?" (o modelo não escolheu) como 0. No piloto da
    versão 2, 8-10% das posições vieram com "?", em geral em "funny" e "informative"; descartar a
    resposta inteira por isso jogava fora 35-49% dos pares. Devolve None se faltar alguma posição."""
    if not isinstance(resposta, str):
        return None
    valores = {int(n): l for n, l in _NUMERADA_COM_VAZIO.findall(resposta)}
    if not all(i in valores for i in range(1, len(METRICAS) + 1)):
        return None
    return [{"A": 1, "B": 2, "?": 0}[valores[i]] for i in range(1, len(METRICAS) + 1)]


def _voto(escolhas, ordem: str) -> np.ndarray:
    """+1 se a escolha foi o segue do Dave, −1 se foi o da The Chain (1 = A, 2 = B, 0 = não escolheu)."""
    e = np.asarray(escolhas, dtype=float)
    dave_e_a = ordem == "dave_primeiro"
    return np.where(e == 0, 0.0, np.where((e == 1) == dave_e_a, 1.0, -1.0))


def preferencias(notas: pd.DataFrame, registros: dict, condicao: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (tabela, consistencia).

    tabela: no formato de notas previstas que `escolha_par.comparar` aceita: para cada par, o
    segue do Dave recebe a preferência (−1 a +1) e o da The Chain recebe 0, de modo que a
    diferença Dave − The Chain é a preferência. Sem coluna `usuario` no E0.
    consistencia: por métrica, % de pares em que as duas ordens escolheram o mesmo segue, e % de
    respostas que não puderam ser lidas.
    """
    por_usuario = condicao != "E0"
    if por_usuario:
        # só pares em que a pessoa avaliou os dois segues (os mesmos de `itens`)
        completos = notas.groupby(["usuario", "segue_idx"])["sistema"].nunique() == 2
        alvos = [(int(u), int(i)) for u, i in completos[completos].index]
    else:
        alvos = [(None, int(i)) for i in sorted(notas["segue_idx"].unique())]
    linhas, iguais, falhas, total = [], np.zeros(len(METRICAS)), 0, 0
    ambas_por_metrica = np.zeros(len(METRICAS))
    for u, idx in alvos:
        votos = []
        for ordem in ORDENS:
            total += 1
            r = registros.get(chave(u, idx, ordem))
            escolhas = ler_escolhas_com_vazio(r.get("resposta")) if r else None
            if escolhas is None and r and r.get("notas"):
                escolhas = r["notas"]
            if escolhas is not None:
                votos.append(_voto(escolhas, ordem))
            else:
                falhas += 1
        pref = np.mean(votos, axis=0) if votos else np.full(len(METRICAS), np.nan)
        if len(votos) == 2:
            decidiu = (votos[0] != 0) & (votos[1] != 0)
            ambas_por_metrica += decidiu
            iguais += (votos[0] == votos[1]) & decidiu
        base = {"usuario": u} if por_usuario else {}
        linhas.append({**base, "segue_idx": idx, "sistema": "dave", **dict(zip(METRICAS, pref))})
        linhas.append({**base, "segue_idx": idx, "sistema": "the_chain", **{m: 0.0 for m in METRICAS}})
    consistencia = pd.DataFrame({"metrica": METRICAS,
                                 "mesma_escolha_nas_duas_ordens_%": 100 * iguais / np.maximum(ambas_por_metrica, 1)})
    consistencia["falhas_%"] = 100 * falhas / max(total, 1)
    return pd.DataFrame(linhas), consistencia
