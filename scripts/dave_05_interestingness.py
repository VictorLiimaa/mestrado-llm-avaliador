"""Dave, passo 5: a nota do próprio Dave (interestingness) contra as notas humanas.

1. Reproduz a única análise do artigo feita sem pessoas novas: correlação de Spearman entre a
   interestingness (e seus componentes) e as notas dos participantes, nos segues do Dave.
2. Experimento offline com treino e teste: aprende os pesos da fórmula com parte dos segues e
   mede nos segues que ficaram de fora; compara com os pesos do artigo, a LLM (E0, se o cache
   existir) e outro participante.
Detalhes em src/avaliador/dave/interestingness.py.

Uso:  python scripts/dave_05_interestingness.py configs/dave/local.yaml
Saída: resultados/dave_artigo/correlacoes_interestingness.md (+ .csv)
       resultados/<experimento>/pesos_aprendidos/resumo.md (+ CSVs)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from avaliador.dave import interestingness as it
from avaliador.dave import juiz, treino_teste
from avaliador.dave.dados import METRICAS, carregar

RAIZ = Path(__file__).resolve().parents[1]
NOMES = {"informativos": "Segues informativos", "engracados": "Segues engraçados"}


def _tabela_artigo(c: pd.DataFrame, categoria: str) -> str:
    d = c[c["categoria"] == categoria].copy()
    d["valor"] = [f"{r:.2f}" + ("+" if p < 0.001 else "") for r, p in zip(d["spearman"], d["p"])]
    return d.pivot(index="metrica", columns="atributo", values="valor")[
        ["interestingness"] + it.COMPONENTES].loc[it.VALENCIA].to_markdown()


def main(caminho_config: str):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    segues, notas = carregar(RAIZ / "dados" / "dave")

    # 1. reprodução do artigo
    c = it.correlacoes_artigo(notas, segues)
    pasta_artigo = RAIZ / "resultados" / "dave_artigo"
    pasta_artigo.mkdir(parents=True, exist_ok=True)
    c.round(4).to_csv(pasta_artigo / "correlacoes_interestingness.csv", index=False)
    texto = ["# Interestingness do Dave contra as notas humanas (reprodução do artigo)\n\n"
             "Spearman entre cada nota de cada participante e a interestingness do segue (e seus "
             "componentes), só nos segues do Dave. `+` = p < 0,001, como no artigo. "
             "Artigo (segues informativos): likeable 0,25, high_quality 0,23, understandable 0,22, "
             "todos p < 0,001; nenhuma correlação significativa nos engraçados.\n"]
    for categoria in ["informativos", "engracados"]:
        texto.append(f"\n## {NOMES[categoria]}\n\n{_tabela_artigo(c, categoria)}\n")
    (pasta_artigo / "correlacoes_interestingness.md").write_text("".join(texto), encoding="utf-8")
    print("".join(texto))

    # 2. pesos aprendidos (treino e teste por segue)
    pasta_cache = RAIZ / "resultados" / cfg["experimento"] / "cache"
    previsores = {"outro_humano": treino_teste.media_outros(notas)}
    for m in cfg["modelos"]:
        arquivo = pasta_cache / f"{m['nome']}__E0.jsonl"
        if arquivo.exists():
            previsores[f"{m['nome']}__E0"] = juiz.tabela_notas(segues, juiz.ler_cache(arquivo)).drop(columns="falha")
    saida = RAIZ / "resultados" / cfg["experimento"] / "pesos_aprendidos"
    saida.mkdir(parents=True, exist_ok=True)
    partes = ["# Pesos da interestingness aprendidos com treino e teste\n\n",
              "Treino e teste por segue (validação cruzada em 5 partes, repetida 10 vezes): um segue de "
              "teste nunca foi visto no treino. Spearman (%) com a nota de cada participante, nos segues do "
              "Dave; IC 95% por bootstrap de participantes; `dif` = diferença para os pesos do artigo "
              "(0,4 / 0,2 / 0,4). Previsor constante conta como 0.\n"]
    for categoria, rotulo in [(None, "Todos os segues do Dave"), ("I", "Só os segues informativos")]:
        comp, pesos = it.validacao_cruzada(notas, segues, previsores, categoria=categoria,
                                           reamostragens=cfg.get("reamostragens_bootstrap", 1000))
        sufixo = "todos" if categoria is None else "informativos"
        comp.round(4).to_csv(saida / f"comparacao_{sufixo}.csv", index=False)
        pesos.round(4).to_csv(saida / f"pesos_{sufixo}.csv", index=False)
        media = comp[comp["metrica"] == "media_8"].set_index("previsor").drop(columns="metrica")
        por_metrica = comp[comp["metrica"] != "media_8"].pivot(index="metrica", columns="previsor",
                                                                values="spearman_%")
        w = pesos.groupby("metrica")[it.COMPONENTES].mean()
        partes += [f"\n## {rotulo}\n\n### Média das 8 métricas (%)\n\n", media.round(1).to_markdown(),
                   "\n\n### Por métrica (Spearman %)\n\n", por_metrica.round(1).to_markdown(),
                   "\n\n### Pesos aprendidos (média entre partes e repetições)\n\n", w.round(2).to_markdown(), "\n"]
        print(f"\n{rotulo}\n{media.round(1).to_string()}")
    (saida / "resumo.md").write_text("".join(partes), encoding="utf-8")
    print(f"\nResumo em {saida / 'resumo.md'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "configs" / "dave" / "mock.yaml"))
