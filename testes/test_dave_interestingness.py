from pathlib import Path

import numpy as np
import pytest

from avaliador.dave import interestingness as it
from avaliador.dave.dados import METRICAS, carregar

PASTA = Path(__file__).resolve().parents[1] / "dados" / "dave"
com_dados = pytest.mark.skipif(not (PASTA / "answers.json").exists(), reason="dados do Dave ausentes")


def test_grade_soma_um():
    g = it.grade_pesos(0.05)
    assert len(g) == 231 and np.allclose(g.sum(axis=1), 1) and (g >= 0).all()


def test_aprender_pesos_recupera_os_pesos_verdadeiros():
    rng = np.random.default_rng(0)
    comp = rng.random((300, 3))
    notas = comp @ np.array([0.7, 0.1, 0.2])
    w = it.aprender_pesos(comp, notas, it.grade_pesos(0.05))
    assert w == pytest.approx([0.7, 0.1, 0.2], abs=0.051)


@com_dados
def test_reproduz_as_correlacoes_do_artigo():
    segues, notas = carregar(PASTA)
    c = it.correlacoes_artigo(notas, segues).set_index(["categoria", "metrica", "atributo"])
    # Artigo, segues informativos: 0,25 / 0,23 / 0,22, todos p < 0,001
    for metrica, valor in [("likeable", 0.25), ("high_quality", 0.23), ("understandable", 0.22)]:
        linha = c.loc[("informativos", metrica, "interestingness")]
        assert round(linha["spearman"], 2) == valor and linha["p"] < 0.001
    # Nenhuma correlação significativa a 0,1% nos engraçados
    assert (c.loc["engracados"].xs("interestingness", level="atributo")["p"] >= 0.001).all()


@com_dados
def test_validacao_cruzada_previsor_perfeito_e_partes():
    segues, notas = carregar(PASTA)
    perfeito = notas[["usuario", "segue_idx", "sistema"] + METRICAS].copy()
    comp, pesos = it.validacao_cruzada(notas, segues, {"perfeito": perfeito}, partes=3, repeticoes=2,
                                       passo=0.25, reamostragens=10)
    assert len(pesos) == 3 * 2 * len(METRICAS)
    media = comp[comp["metrica"] == "media_8"].set_index("previsor")
    assert media.loc["perfeito", "spearman_%"] == pytest.approx(100)
