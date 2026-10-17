from pathlib import Path

import pytest

from avaliador.lu.dados import ASPECTOS, carregar
from avaliador.lu.metaavaliacao import correlacao_3_niveis
from avaliador.lu.prompts import DESCRICOES, montar_prompt, preferencias_gerais

PASTA = Path(__file__).resolve().parents[1] / "dados" / "lu"
pytestmark = pytest.mark.skipif(not (PASTA / "df_explanation.pkl").exists(),
                                reason="dados do Lu ausentes: rode scripts/dados_baixar_lu.py")


@pytest.fixture(scope="module")
def df():
    return carregar(PASTA)


def test_dados_alinhados(df):
    assert len(df) == 2536
    assert df["user"].nunique() == 39
    for a in ASPECTOS:
        assert df[f"user_{a}"].between(1, 5).all()


def test_correlacao_perfeita(df):
    d = df.copy()
    d["copia_persuasiveness"] = d["user_persuasiveness"]
    r = correlacao_3_niveis(d, "user_persuasiveness", "copia_persuasiveness")
    assert r["dataset"] == pytest.approx(1.0)
    assert r["user"] == pytest.approx(1.0)
    assert r["pair"] == pytest.approx(1.0)


def test_e3_nao_usa_o_filme_avaliado(df):
    """Contra vazamento: as preferências do E3 vêm só dos outros filmes do usuário."""
    linha = df.iloc[0]
    pos, neg = preferencias_gerais(df, linha["user"], linha["movie_id"])
    so_este_filme = df[(df["user"] == linha["user"]) & (df["movie_id"] == linha["movie_id"])]
    outros = df[(df["user"] == linha["user"]) & (df["movie_id"] != linha["movie_id"])]
    atributos_outros = {
        (t if v == "1" else f"{t}: {v}")
        for lista in outros["self_attributes"] for item in lista
        for t, v, _ in [str(item).split("=")] if len(str(item).split("=")) == 3
    }
    for atributo in pos + neg:
        assert atributo in atributos_outros
    assert len(so_este_filme) > 0


def test_prompt_sem_vazamento(df):
    linha = df.iloc[0]
    prompt = montar_prompt(df, linha, "E3")
    assert linha["self_explanation"] not in prompt


def test_bug_de_transparencia_corrigido_por_padrao(df):
    linha = df.iloc[0]
    corrigido = montar_prompt(df, linha, "E0")
    original = montar_prompt(df, linha, "E0", reproduzir_bug_transparencia=True)
    assert f"Transparency: {DESCRICOES['transparency']}" in corrigido
    assert f"Transparency: {DESCRICOES['persuasiveness']}" in original


def test_condicoes_isoladas(df):
    linha = df.iloc[0]
    so_resumo = montar_prompt(df, linha, "so_resumo")
    assert "taste in movies" in so_resumo and "Your gender" not in so_resumo
    so_pref = montar_prompt(df, linha, "so_preferencias")
    assert "In other movies" in so_pref and "taste in movies" not in so_pref


def test_resposta_curta(df):
    linha = df.iloc[0]
    assert "ONLY the four integers" in montar_prompt(df, linha, "E0", resposta_curta=True)


def test_niveis_sao_cumulativos(df):
    linha = df.iloc[0]
    tamanhos = [len(montar_prompt(df, linha, n)) for n in ["E0", "E1", "E2", "E3"]]
    assert tamanhos == sorted(tamanhos)


def test_condicoes_foco(df):
    linha = df.iloc[0]
    sem = montar_prompt(df, linha, "so_resumo")
    com = montar_prompt(df, linha, "foco_resumo")
    assert "judge only the quality" in com and "judge only the quality" not in sem
    assert com.replace(com[com.index("Important:"):com.index("Please rate")], "") == sem
    assert "profile" not in montar_prompt(df, linha, "foco_E0").split("Important:")[0]
