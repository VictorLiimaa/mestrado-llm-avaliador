"""Teste offline de treino e teste no Dave: a LLM consegue prever as notas de UM participante?

Cada participante avaliou 3 pares de segues (a mesma música inicial, um segue do Dave e um da
The Chain). Para cada participante e cada par, esse par é o TESTE e os outros pares são o
TREINO (leave-one-pair-out): todas as notas viram teste uma vez, e o par testado nunca aparece
no treino (nem o segue do outro sistema, que tem a mesma música inicial).

A nota de uma pessoa tem duas partes: o "jeito" dela (quem dá "Agree" para tudo) e a reação ao
segue. Por isso comparamos cada previsor em duas medidas:
- Pearson com a nota (pearson_%): tudo junto;
- Pearson dentro do participante (centrada_%): de cada participante, tiramos a média dele da
  nota real E da previsão, e só então correlacionamos. O "jeito" sai da conta dos dois lados;
  sobra se o previsor ordena bem os segues DAQUELA pessoa. Atenção: a media_usuario sai negativa
  nessa medida por construção (quando o par de teste tem notas altas, tirá-lo baixa a média do
  treino), ou seja, ela não sabe nada sobre os segues; só sobre a pessoa.

Previsores sem LLM:
- media_usuario: média do participante nos pares de treino, na mesma métrica (só o "jeito");
- outro_humano: média dos outros participantes que viram o mesmo segue (só o segue);
- usuario_mais_segue: soma dos dois (como Pearson ignora constantes, a soma basta).
Previsores com LLM: E0 (só o segue, a mesma nota para todos) e as condições de CONDICOES_OUVINTE,
com informação sobre o participante no prompt (histórico, perfil, familiaridade e combinações).

Todos os previsores são comparados nas MESMAS linhas: segues vistos por 2+ participantes (para
o outro_humano existir) e sem falha de leitura em nenhum previsor.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..comum import execucao
from ..comum.correlacao import pearson, pearson_ic
from ..comum.llm import LLM
from .dados import METRICAS
from .prompts import montar_prompt_ouvinte

CAMPO_CHAVE = "chave"
CHAVES = ["usuario", "segue_idx", "sistema"]
FAMILIARIDADE = ["conhece_musica1", "conhece_artista1", "conhece_musica2", "conhece_artista2"]

# O que cada condição põe no prompt: (histórico, perfil, familiaridade).
CONDICOES_OUVINTE = {
    "historico": (True, False, False),
    "perfil": (False, True, False),
    "familiaridade": (False, False, True),
    "perfil_familiaridade": (False, True, True),
    "completo": (True, True, True),
}


def chave(usuario, segue_idx, sistema) -> str:
    return f"{int(usuario)}_{int(segue_idx)}_{sistema}"


# ---------------------------------------------------------------- divisão treino / teste
def treino_de(notas: pd.DataFrame, usuario: int, segue_idx: int) -> pd.DataFrame:
    """Notas do participante em todos os pares, menos o par de teste, na ordem em que as viu."""
    d = notas[(notas["usuario"] == usuario) & (notas["segue_idx"] != segue_idx)]
    return d.sort_values("posicao")


def itens(notas: pd.DataFrame, segues: pd.DataFrame, perfis: dict | None = None,
          familiaridade: pd.DataFrame | None = None) -> list[dict]:
    """Um item por nota humana: o segue de teste, os exemplos de treino do mesmo participante e,
    se fornecidos, o perfil dele e o que ele conhecia de cada segue (teste e treino)."""
    por_segue = segues.set_index(["segue_idx", "sistema"])
    fam = None
    if familiaridade is not None:
        fam = familiaridade.set_index(["usuario", "posicao"])[FAMILIARIDADE].to_dict("index")
    saida = []
    for _, linha in notas.iterrows():
        u, pos = int(linha["usuario"]), int(linha["posicao"])
        treino = treino_de(notas, u, linha["segue_idx"])
        saida.append({
            "usuario": u, "segue_idx": int(linha["segue_idx"]), "sistema": linha["sistema"],
            "segue": por_segue.loc[(linha["segue_idx"], linha["sistema"])],
            "treino": [(por_segue.loc[(t["segue_idx"], t["sistema"])], [t[m] for m in METRICAS],
                        fam.get((u, int(t["posicao"]))) if fam else None)
                       for _, t in treino.iterrows()],
            "perfil": perfis.get(u) if perfis else None,
            "familiaridade": fam.get((u, pos)) if fam else None,
        })
    return saida


def montar(item: dict, condicao: str, resposta_curta: bool = True) -> str:
    if condicao not in CONDICOES_OUVINTE:
        raise ValueError(f"Condição desconhecida: {condicao}. Opções: {list(CONDICOES_OUVINTE)}")
    com_historico, com_perfil, com_familiaridade = CONDICOES_OUVINTE[condicao]
    if com_perfil and item["perfil"] is None or com_familiaridade and item["familiaridade"] is None:
        raise ValueError(f"A condição {condicao} precisa de perfis e familiaridade em `itens`.")
    return montar_prompt_ouvinte(
        item["segue"],
        perfil=item["perfil"] if com_perfil else None,
        familiaridade=item["familiaridade"] if com_familiaridade else None,
        treino=item["treino"] if com_historico else None,
        resposta_curta=resposta_curta,
    )


# ---------------------------------------------------------------- LLM
def avaliar(notas: pd.DataFrame, segues: pd.DataFrame, llm: LLM, arquivo_cache: str | Path,
            condicao: str = "historico", perfis: dict | None = None,
            familiaridade: pd.DataFrame | None = None, resposta_curta: bool = True,
            paralelo: int = 1, progresso: bool = True) -> dict:
    return execucao.executar(
        itens=itens(notas, segues, perfis, familiaridade),
        chave=lambda i: chave(i["usuario"], i["segue_idx"], i["sistema"]),
        montar_prompt=lambda i: montar(i, condicao, resposta_curta),
        llm=llm, arquivo=arquivo_cache, campo_chave=CAMPO_CHAVE, n_notas=len(METRICAS),
        condicao=condicao, paralelo=paralelo, progresso=progresso,
    )


def ler_cache(arquivo_cache: str | Path) -> dict:
    return execucao.ler_cache(arquivo_cache, CAMPO_CHAVE)


def tabela_notas(notas: pd.DataFrame, registros: dict) -> pd.DataFrame:
    """Uma linha por nota humana com as 8 notas previstas pela LLM (NaN se não pôde ser lida)."""
    linhas = []
    for _, n in notas.iterrows():
        r = registros.get(chave(n["usuario"], n["segue_idx"], n["sistema"]))
        previstas = r["notas"] if r else None
        linha = {"usuario": n["usuario"], "segue_idx": n["segue_idx"], "sistema": n["sistema"],
                 "falha": previstas is None}
        for i, m in enumerate(METRICAS):
            linha[m] = previstas[i] if previstas else np.nan
        linhas.append(linha)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- previsores sem LLM
def media_usuario_treino(notas: pd.DataFrame) -> pd.DataFrame:
    """Para cada nota, a média do mesmo participante na mesma métrica, fora do par de teste."""
    saida = notas[CHAVES].copy()
    for m in METRICAS:
        g_u = notas.groupby("usuario")[m]
        g_up = notas.groupby(["usuario", "segue_idx"])[m]
        soma = g_u.transform("sum") - g_up.transform("sum")
        n = g_u.transform("count") - g_up.transform("count")
        saida[m] = (soma / n.where(n > 0)).to_numpy(float)
    return saida


def media_outros(notas: pd.DataFrame) -> pd.DataFrame:
    """Para cada nota, a média dos OUTROS participantes que viram o mesmo segue."""
    saida = notas[CHAVES].copy()
    for m in METRICAS:
        g = notas.groupby(["segue_idx", "sistema"])[m]
        n = g.transform("count") - notas[m].notna()
        saida[m] = ((g.transform("sum") - notas[m].fillna(0)) / n.where(n > 0)).to_numpy(float)
    return saida


def previsores_sem_llm(notas: pd.DataFrame) -> dict[str, pd.DataFrame]:
    usuario, outros = media_usuario_treino(notas), media_outros(notas)
    soma = usuario.copy()
    soma[METRICAS] = usuario[METRICAS].to_numpy(float) + outros[METRICAS].to_numpy(float)
    return {"media_usuario": usuario, "outro_humano": outros, "usuario_mais_segue": soma}


# ---------------------------------------------------------------- comparação
def _alinhar(notas: pd.DataFrame, previsores: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Tabela larga: nota real e a previsão de cada previsor.
    Previsores sem coluna `usuario` (ex.: E0) dão a mesma nota a todos que viram o segue."""
    df = notas[CHAVES + METRICAS].copy()
    for nome, p in previsores.items():
        chaves = [c for c in CHAVES if c in p.columns]
        p = p[chaves + METRICAS].rename(columns={m: f"{m}__{nome}" for m in METRICAS})
        df = df.merge(p, on=chaves, how="left")
    return df


MEDIA = "media_8"


def comparar(notas: pd.DataFrame, previsores: dict[str, pd.DataFrame], referencia: str = "media_usuario",
             reamostragens: int = 1000, semente: int = 2026) -> pd.DataFrame:
    """Pearson (%) de cada previsor com a nota e com a nota centrada, por métrica e na média das
    8 métricas (linha `media_8`), com IC 95% por bootstrap de participantes, e a diferença para
    o previsor de `referencia`, também com IC.

    Em cada reamostragem, os MESMOS participantes sorteados valem para todas as métricas e todos
    os previsores; assim o IC da média e o IC da diferença respeitam essas dependências.
    """
    if referencia not in previsores:
        raise ValueError(f"Previsor de referência ausente: {referencia}")
    df = _alinhar(notas, previsores)
    nomes = list(previsores)
    tipos = ("bruta", "centrada", "dif")

    por_metrica = {}
    for m in METRICAS:
        colunas = [m] + [f"{m}__{n}" for n in nomes]
        d = df.dropna(subset=colunas).reset_index(drop=True)
        g = d.groupby("usuario")
        sem_media = lambda col: (d[col] - g[col].transform("mean")).to_numpy(float)
        usuarios_d = d["usuario"].to_numpy()
        por_metrica[m] = {
            "real": d[m].to_numpy(float),
            "real_c": sem_media(m),
            "prev": {n: d[f"{m}__{n}"].to_numpy(float) for n in nomes},
            "prev_c": {n: sem_media(f"{m}__{n}") for n in nomes},
            "idx_u": {u: np.flatnonzero(usuarios_d == u) for u in np.unique(usuarios_d)},
        }

    def medir(dados: dict, idx) -> dict:
        real, real_c = dados["real"][idx], dados["real_c"][idx]
        r_ref = pearson(real, dados["prev"][referencia][idx])
        saida = {}
        for n in nomes:
            r = pearson(real, dados["prev"][n][idx])
            saida[n] = {"bruta": r, "centrada": pearson(real_c, dados["prev_c"][n][idx]), "dif": r - r_ref}
        return saida

    todos = np.unique(df["usuario"].to_numpy())
    rng = np.random.default_rng(semente)
    boot = {m: {n: {t: [] for t in tipos} for n in nomes} for m in METRICAS + [MEDIA]}
    for _ in range(reamostragens):
        sorteados = rng.choice(todos, len(todos))
        acumulado = {n: {t: [] for t in tipos} for n in nomes}
        for m, dados in por_metrica.items():
            idx = np.concatenate([dados["idx_u"][u] for u in sorteados if u in dados["idx_u"]])
            for n, valores in medir(dados, idx).items():
                for t in tipos:
                    boot[m][n][t].append(valores[t])
                    acumulado[n][t].append(valores[t])
        for n in nomes:
            for t in tipos:
                boot[MEDIA][n][t].append(np.nanmean(acumulado[n][t]))

    pontos = {m: medir(d, np.arange(len(d["real"]))) for m, d in por_metrica.items()}
    pontos[MEDIA] = {n: {t: float(np.nanmean([pontos[m][n][t] for m in METRICAS])) for t in tipos}
                     for n in nomes}
    linhas = []
    for m in METRICAS + [MEDIA]:
        for n in nomes:
            ic = lambda t, q: 100 * np.nanpercentile(boot[m][n][t], q)
            v = pontos[m][n]
            linhas.append({
                "metrica": m, "previsor": n,
                "pearson_%": 100 * v["bruta"], "ic_inf_%": ic("bruta", 2.5), "ic_sup_%": ic("bruta", 97.5),
                "centrada_%": 100 * v["centrada"], "centrada_ic_inf_%": ic("centrada", 2.5),
                "centrada_ic_sup_%": ic("centrada", 97.5),
                f"dif_vs_{referencia}_%": 100 * v["dif"],
                "dif_ic_inf_%": ic("dif", 2.5), "dif_ic_sup_%": ic("dif", 97.5),
                "n": len(por_metrica[m]["real"]) if m in por_metrica else None,
            })
    return pd.DataFrame(linhas)


def efeito_familiaridade(notas: pd.DataFrame, familiaridade: pd.DataFrame) -> pd.DataFrame:
    """Sem LLM: quanto conhecer as músicas/artistas se liga às notas, DENTRO de cada participante
    (Pearson %, com a média de cada pessoa retirada dos dois lados). Mostra se há sinal para o
    enriquecimento aproveitar; o artigo do Dave (Tabela 7) relata efeito da familiaridade."""
    d = notas.merge(familiaridade, on=["usuario", "posicao"])
    linhas = []
    for col in FAMILIARIDADE:
        linha = {"conhece": col}
        for m in METRICAS:
            x = d[["usuario", col, m]].dropna().astype({col: float})
            g = x.groupby("usuario")
            a = (x[col] - g[col].transform("mean")).to_numpy(float)
            b = (x[m] - g[m].transform("mean")).to_numpy(float)
            linha[m] = 100 * pearson(a, b)
        linha["% que conhece"] = 100 * d[col].dropna().astype(float).mean()
        linhas.append(linha)
    return pd.DataFrame(linhas).set_index("conhece")
