from pathlib import Path

import pandas as pd
import pytest

from avaliador.dave import escolha_par
from avaliador.dave.dados import METRICAS, carregar

PASTA = Path(__file__).resolve().parents[1] / "dados" / "dave"
pytestmark = pytest.mark.skipif(not (PASTA / "answers.json").exists(), reason="dados do Dave ausentes")


def test_jeito_da_pessoa_se_cancela_e_previsor_perfeito():
    _, notas = carregar(PASTA)
    perfeito = notas[["usuario", "segue_idx", "sistema"] + METRICAS].copy()
    deslocado = perfeito.copy()
    deslocado[METRICAS] = deslocado[METRICAS] + deslocado[["usuario"]].to_numpy() % 3   # "jeito"
    t = escolha_par.comparar(notas, {"perfeito": perfeito, "deslocado": deslocado}, reamostragens=10)
    media = t[t["metrica"] == escolha_par.MEDIA].set_index("previsor")
    assert media.loc["perfeito", "correlacao_%"] == pytest.approx(100)
    assert media.loc["perfeito", "acordo_%"] == pytest.approx(100)
    # somar uma constante por pessoa não muda a preferência no par
    assert media.loc["deslocado", "correlacao_%"] == pytest.approx(100)


def test_previsor_constante_sempre_empata():
    segues, notas = carregar(PASTA)
    constante = segues[["segue_idx", "sistema"]].assign(**{m: 3.0 for m in METRICAS})
    t = escolha_par.comparar(notas, {"constante": constante}, reamostragens=10)
    media = t[t["metrica"] == escolha_par.MEDIA].set_index("previsor")
    assert media.loc["constante", "empate_%"] == pytest.approx(100)
    assert media.loc["constante", "correlacao_%"] == pytest.approx(0)
