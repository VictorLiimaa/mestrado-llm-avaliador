from pathlib import Path

import numpy as np
import pytest

from avaliador.comum.llm import ler_escolhas
from avaliador.dave import par_direto
from avaliador.dave.dados import METRICAS, carregar, carregar_familiaridade, carregar_perfis

PASTA = Path(__file__).resolve().parents[1] / "dados" / "dave"
com_dados = pytest.mark.skipif(not (PASTA / "answers.json").exists(), reason="dados do Dave ausentes")


@pytest.mark.parametrize("resposta,esperado", [
    ("A B A A B B A A", [1, 2, 1, 1, 2, 2, 1, 1]),
    ("1:A 2:B 3:A 4:A 5:B 6:B 7:A 8:A", [1, 2, 1, 1, 2, 2, 1, 1]),
    ("Segue A wins.\n1: B\n2: B\n3: A\n4: A\n5: B\n6: A\n7: A\n8: B", [2, 2, 1, 1, 2, 1, 1, 2]),
    ("1:A 2:B 3:A", None),
    ("Segue A is better.\nA A A A B B B B", [1, 1, 1, 1, 2, 2, 2, 2]),
    ("3 3 3 3 3 3 3 3", None),
    ("A B", None),
])
def test_ler_escolhas(resposta, esperado):
    assert ler_escolhas(resposta, 8) == esperado


def test_voto_respeita_a_ordem():
    assert list(par_direto._voto([1, 2], "dave_primeiro")) == [1, -1]
    assert list(par_direto._voto([1, 2], "chain_primeiro")) == [-1, 1]


@com_dados
def test_vies_de_posicao_vira_empate_e_preferencia_consistente_vale_um():
    segues, notas = carregar(PASTA)
    pares = notas.groupby(["usuario", "segue_idx"])["sistema"].nunique()
    pares = [(u, i) for (u, i), k in pares.items() if k == 2]
    sempre_a = {par_direto.chave(u, i, o): {"notas": [1] * 8} for u, i in pares for o in par_direto.ORDENS}
    t, c = par_direto.preferencias(notas, sempre_a, "perfil")
    assert (t[t["sistema"] == "dave"][METRICAS] == 0).all().all()
    assert (c["mesma_escolha_nas_duas_ordens_%"] == 0).all()
    sempre_dave = {par_direto.chave(u, i, o): {"notas": [1 if o == "dave_primeiro" else 2] * 8}
                   for u, i in pares for o in par_direto.ORDENS}
    t, c = par_direto.preferencias(notas, sempre_dave, "perfil")
    assert (t[t["sistema"] == "dave"][METRICAS] == 1).all().all()
    assert (c["mesma_escolha_nas_duas_ordens_%"] == 100).all()


@com_dados
def test_itens_nas_duas_ordens_e_sem_o_par_no_historico():
    segues, notas = carregar(PASTA)
    itens = par_direto.itens(notas, segues, "completo", carregar_perfis(PASTA), carregar_familiaridade(PASTA))
    assert len(itens) % 2 == 0 and {i["ordem"] for i in itens} == set(par_direto.ORDENS)
    dave = segues.set_index(["segue_idx", "sistema"])
    for item in itens[:40]:
        texto_dave = dave.loc[(item["segue_idx"], "dave"), "texto"]
        a = item["prompt"].split("Segue A: ")[1].split("\n")[0]
        assert (a == texto_dave) == (item["ordem"] == "dave_primeiro")
        # no histórico (antes da comparação) não aparece nenhum segue do par de teste
        historico = item["prompt"].split("Now compare")[0]
        primeira = dave.loc[(item["segue_idx"], "dave"), "musica1"]
        assert f"First track: {primeira} by" not in historico


def test_prompt_par_sem_exemplo_de_resposta():
    import pandas as pd
    from avaliador.dave.prompts import FORMATO_PAR, montar_prompt_par
    s = pd.Series({"musica1": "M1", "artista1": "X", "musica2": "M2", "artista2": "Y", "texto": "T"})
    p = montar_prompt_par(s, s)
    assert p.endswith(FORMATO_PAR) and "Example" not in p
    assert ler_escolhas(FORMATO_PAR, 8) is None          # o próprio molde não é uma resposta válida


def test_interrogacao_vira_nao_escolheu():
    assert par_direto.ler_escolhas_com_vazio("1:A 2:B 3:? 4:A 5:? 6:B 7:A 8:B") == [1, 2, 0, 1, 0, 2, 1, 2]
    assert par_direto.ler_escolhas_com_vazio("1:A 2:B") is None
    assert list(par_direto._voto([0, 1, 2], "dave_primeiro")) == [0, 1, -1]
