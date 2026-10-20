from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from avaliador.dave import treino_teste
from avaliador.dave.dados import METRICAS, carregar
from avaliador.dave.prompts import montar_prompt_historico

PASTA = Path(__file__).resolve().parents[1] / "dados" / "dave"


def _notas_sinteticas(semente=0):
    """4 participantes x 3 pares x 2 sistemas, segues compartilhados entre participantes."""
    rng = np.random.default_rng(semente)
    linhas = []
    for u in range(4):
        for posicao, par in enumerate([10 + u % 2, 20, 30 + u % 2]):
            for k, sistema in enumerate(["dave", "the_chain"]):
                linha = {"usuario": u, "segue_idx": par, "sistema": sistema, "posicao": 2 * posicao + k}
                linha.update({m: int(rng.integers(1, 6)) for m in METRICAS})
                linhas.append(linha)
    return pd.DataFrame(linhas)


def test_media_usuario_exclui_o_par_de_teste():
    notas = _notas_sinteticas()
    prev = treino_teste.media_usuario_treino(notas)
    for i in [0, 7, 13]:
        u, par = notas.loc[i, "usuario"], notas.loc[i, "segue_idx"]
        treino = notas[(notas["usuario"] == u) & (notas["segue_idx"] != par)]
        assert prev.loc[i, "likeable"] == pytest.approx(treino["likeable"].mean())


def test_media_outros_exclui_a_propria_nota():
    notas = _notas_sinteticas()
    prev = treino_teste.media_outros(notas)
    mesmos = notas[(notas["segue_idx"] == 20) & (notas["sistema"] == "dave")]
    i = mesmos.index[0]
    assert prev.loc[i, "funny"] == pytest.approx(mesmos.drop(index=i)["funny"].mean())


def test_comparar_previsor_perfeito_e_referencia():
    notas = _notas_sinteticas()
    perfeito = notas[treino_teste.CHAVES + METRICAS].copy()
    previsores = treino_teste.previsores_sem_llm(notas) | {"perfeito": perfeito}
    t = treino_teste.comparar(notas, previsores, reamostragens=20).set_index(["metrica", "previsor"])
    media = t.loc[treino_teste.MEDIA]
    assert media.loc["perfeito", "pearson_%"] == pytest.approx(100)
    assert media.loc["perfeito", "centrada_%"] == pytest.approx(100)
    assert media.loc["media_usuario", "dif_vs_media_usuario_%"] == pytest.approx(0)


def test_prompt_historico_mostra_notas_do_treino():
    segue = pd.Series({"musica1": "A", "artista1": "X", "musica2": "B", "artista2": "Y",
                       "texto": "TESTE"})
    treino = [(pd.Series({"musica1": "C", "artista1": "Z", "musica2": "D", "artista2": "W",
                          "texto": "TREINO"}), [4, 4, 5, 3, 2, None, 4, 1])]
    p = montar_prompt_historico(segue, treino)
    assert "Your ratings: 4 4 5 3 2 - 4 1" in p
    assert p.index("TREINO") < p.index("TESTE")


@pytest.mark.skipif(not (PASTA / "answers.json").exists(), reason="dados do Dave ausentes")
def test_treino_nunca_contem_o_par_de_teste():
    segues, notas = carregar(PASTA)
    itens = treino_teste.itens(notas, segues)
    assert len(itens) == len(notas)
    for item in itens:
        assert item["treino"], "todo participante tem outros pares"
        assert all(t[0].name[0] != item["segue_idx"] for t in item["treino"])
        # o mesmo texto de segue pode se repetir em pares diferentes; o bloco inteiro, não
        s = item["segue"]
        bloco = f"First track: {s['musica1']} by {s['artista1']}\nSegue: {s['texto']}"
        anteriores = montar_prompt_historico(s, item["treino"]).split("Now rate this new segue")[0]
        assert bloco not in anteriores


@pytest.mark.skipif(not (PASTA / "answers.json").exists(), reason="dados do Dave ausentes")
def test_familiaridade_e_perfis():
    from avaliador.dave.dados import carregar_familiaridade, carregar_perfis
    segues, notas = carregar(PASTA)
    fam = carregar_familiaridade(PASTA)
    perfis = carregar_perfis(PASTA)
    assert set(notas["usuario"]) <= set(perfis)
    # Os dois segues de um par têm a mesma primeira música: a mesma resposta de familiaridade.
    juntos = notas.merge(fam, on=["usuario", "posicao"])
    por_par = juntos.groupby(["usuario", "segue_idx"])["conhece_musica1"].nunique(dropna=False)
    assert (por_par == 1).all()
    # Perfil: 7 itens do Gold-MSI + shows + tempo de escuta + inglês, em texto.
    assert max(len(p) for p in perfis.values()) == 10


@pytest.mark.skipif(not (PASTA / "answers.json").exists(), reason="dados do Dave ausentes")
def test_condicoes_poem_so_o_que_devem_no_prompt():
    from avaliador.dave.dados import carregar_familiaridade, carregar_perfis
    segues, notas = carregar(PASTA)
    item = treino_teste.itens(notas, segues, carregar_perfis(PASTA), carregar_familiaridade(PASTA))[0]
    tem = lambda p: ("Your ratings" in p, "About you" in p, "Before the survey you said" in p)
    assert tem(treino_teste.montar(item, "historico")) == (True, False, False)
    assert tem(treino_teste.montar(item, "perfil")) == (False, True, False)
    assert tem(treino_teste.montar(item, "familiaridade")) == (False, False, True)
    assert tem(treino_teste.montar(item, "completo")) == (True, True, True)
    with pytest.raises(ValueError):
        treino_teste.montar(treino_teste.itens(notas, segues)[0], "perfil")
