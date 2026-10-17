import numpy as np
import pytest

from avaliador.comum import execucao
from avaliador.comum.correlacao import correlacao, kendall, pearson, pearson_ic, spearman
from avaliador.comum.estatistica import ttest_independente, ttest_pareado
from avaliador.comum.llm import ConfigModelo, MockLLM, ler_notas


@pytest.mark.parametrize("resposta,esperado", [
    ("My ratings: 4 3 5 2", [4, 3, 5, 2]),
    ("Persuasiveness 4\nTransparency 5\nAccuracy 3\nSatisfactory 4\n\n4 5 3 4", [4, 5, 3, 4]),
    ("I would give 10 out of 10", None),
    ("3 3", None),
    (None, None),
])
def test_ler_notas(resposta, esperado):
    assert ler_notas(resposta) == esperado


def test_ler_notas_quantidade():
    assert ler_notas("1 2 3 4 5 1 2 3", quantidade=8) == [1, 2, 3, 4, 5, 1, 2, 3]


def test_correlacao_constante_e_nan():
    assert np.isnan(correlacao([3, 3, 3], [1, 2, 3]))


def test_correlacoes_batem_com_scipy():
    stats = pytest.importorskip("scipy.stats")  # pula se o scipy estiver ausente ou bloqueado
    rng = np.random.default_rng(0)
    for _ in range(20):
        a = rng.integers(1, 6, size=60).astype(float)
        b = (a + rng.integers(-2, 3, size=60)).astype(float)
        assert pearson(a, b) == pytest.approx(stats.pearsonr(a, b)[0])
        assert spearman(a, b) == pytest.approx(stats.spearmanr(a, b)[0])
        assert kendall(a, b) == pytest.approx(stats.kendalltau(a, b)[0])


def test_pearson_ic_bate_com_scipy():
    stats = pytest.importorskip("scipy.stats")
    rng = np.random.default_rng(2)
    for n in [3, 4, 10, 60, 800]:
        a = rng.integers(1, 6, n).astype(float)
        b = (a + rng.integers(-3, 4, n)).astype(float)
        nosso, ref = pearson_ic(a, b), stats.pearsonr(a, b)
        for confianca in (0.95, 0.90):
            ic = ref.confidence_interval(confianca)
            meu = pearson_ic(a, b, confianca)
            assert (meu.ic_inf, meu.ic_sup) == pytest.approx((ic.low, ic.high))
        assert (nosso.r, nosso.p) == pytest.approx((ref.statistic, ref.pvalue))


def test_pearson_ic_sem_scipy():
    """Valores fixos obtidos com scipy 1.18, para conferir mesmo onde o scipy é bloqueado."""
    r = pearson_ic([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [2, 1, 4, 3, 6, 5, 8, 7, 10, 9])
    assert r.r == pytest.approx(0.9393939, abs=1e-6)
    assert r.p == pytest.approx(5.48405e-05, rel=1e-4)
    assert (r.ic_inf, r.ic_sup) == pytest.approx((0.758244, 0.985895), abs=1e-6)
    assert np.isnan(pearson_ic([1, 1, 1, 1], [1, 2, 3, 4]).r)


def test_ttest_bate_com_scipy():
    stats = pytest.importorskip("scipy.stats")
    rng = np.random.default_rng(1)
    a, b = rng.integers(1, 6, 50).astype(float), rng.integers(1, 6, 50).astype(float)
    assert np.allclose(ttest_pareado(a, b), tuple(stats.ttest_rel(a, b)))
    assert np.allclose(ttest_independente(a, b[:40]), tuple(stats.ttest_ind(a, b[:40])))


def test_execucao_retoma_do_cache(tmp_path):
    """Uma segunda execução não chama a LLM de novo para itens que já estão no arquivo."""
    chamadas = []

    class Contador(MockLLM):
        def gerar(self, prompt):
            chamadas.append(prompt)
            return super().gerar(prompt)

    llm = Contador(ConfigModelo(nome="m", backend="mock"))
    arquivo = tmp_path / "cache.jsonl"
    argumentos = dict(chave=lambda i: i, montar_prompt=lambda i: f"item {i}", llm=llm,
                      arquivo=arquivo, campo_chave="id", n_notas=4, condicao="E0")
    execucao.executar(itens=[1, 2], **argumentos)
    registros = execucao.executar(itens=[1, 2, 3], **argumentos)
    assert len(chamadas) == 3 and set(registros) == {1, 2, 3}
    assert all(len(r["notas"]) == 4 for r in registros.values())
