from pathlib import Path

import pytest

from avaliador.dave.avaliacao import tabela_artigo
from avaliador.dave.dados import FRASES, carregar
from avaliador.dave.prompts import montar_prompt

PASTA = Path(__file__).resolve().parents[1] / "dados" / "dave"
pytestmark = pytest.mark.skipif(not (PASTA / "answers.json").exists(),
                                reason="dados do Dave ausentes: rode scripts/dados_preparar_dave.py")


@pytest.fixture(scope="module")
def dados():
    return carregar(PASTA)


def test_dados_e_tabela_do_artigo(dados):
    segues, notas = dados
    assert len(segues) == 344 and segues["categoria"].notna().all()
    t = tabela_artigo(notas).set_index(["grupo", "metrica"])
    # Valores do notebook dos autores: segues informativos, "informative" 3,73 x 3,43 (p < 0,01)
    assert round(t.loc[("informativos", "informative"), "dave"], 2) == 3.73
    assert round(t.loc[("informativos", "informative"), "the_chain"], 2) == 3.43
    assert 0.001 <= t.loc[("informativos", "informative"), "p"] < 0.01


def test_prompt_tem_as_8_frases(dados):
    segues, _ = dados
    p = montar_prompt(segues.iloc[0])
    assert all(f in p for f in FRASES.values()) and segues.iloc[0]["texto"] in p
