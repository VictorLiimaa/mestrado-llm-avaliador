"""Dave, passo 6: escolha no par. Dos dois segues de um par, qual a pessoa preferiu, e a LLM aponta o mesmo?

Usa as respostas que já estão no cache (E0 e as condições do passo 4); não chama a LLM.
Na diferença Dave − The Chain de uma mesma pessoa, o "jeito" dela se cancela: sobra só a
preferência. Detalhes em src/avaliador/dave/escolha_par.py.

Uso:  python scripts/dave_06_escolha_par.py configs/dave/local.yaml
Saída: resultados/<experimento>/escolha_par/resumo.md e comparacao.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from avaliador.dave import escolha_par, juiz, treino_teste
from avaliador.dave.dados import METRICAS, carregar

RAIZ = Path(__file__).resolve().parents[1]


def main(caminho_config: str):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    segues, notas = carregar(RAIZ / "dados" / "dave")
    pasta = RAIZ / "resultados" / cfg["experimento"]
    condicoes = ["E0"] + (cfg.get("treino_teste") or {}).get("condicoes", ["historico"])

    tabelas = {}
    for m in cfg["modelos"]:
        for condicao in condicoes:
            arquivo = pasta / "cache" / f"{m['nome']}__{condicao}.jsonl"
            if not arquivo.exists():
                continue
            if condicao == "E0":
                t = juiz.tabela_notas(segues, juiz.ler_cache(arquivo))
            else:
                t = treino_teste.tabela_notas(notas, treino_teste.ler_cache(arquivo))
            tabelas[(m["nome"], condicao)] = t.drop(columns="falha")
    previsores = {f"{nome}__{c}": t for (nome, c), t in tabelas.items()}
    for comb in cfg.get("combinacao", []) or []:
        for condicao in condicoes:
            partes = [tabelas.get((n, condicao)) for n in comb["modelos"]]
            if all(p is not None for p in partes):
                media = partes[0].copy()
                media[METRICAS] = np.mean([p[METRICAS].to_numpy(float) for p in partes], axis=0)
                previsores[f"{comb['nome']}__{condicao}"] = media
    if not previsores:
        print("Nenhuma resposta de LLM no cache; rode antes o dave_02 e o dave_04.")
        return

    t = escolha_par.comparar(notas, previsores, cfg.get("reamostragens_bootstrap", 1000))
    saida = pasta / "escolha_par"
    saida.mkdir(parents=True, exist_ok=True)
    t.round(4).to_csv(saida / "comparacao.csv", index=False)
    media = t[t["metrica"] == escolha_par.MEDIA].set_index("previsor").drop(columns=["metrica", "pares"])
    por_metrica = t[t["metrica"] != escolha_par.MEDIA].pivot(index="metrica", columns="previsor",
                                                             values="correlacao_%")
    texto = [
        f"# Escolha no par: {cfg['experimento']}\n\n",
        "Para cada participante e par, a preferência é a diferença de notas Dave − The Chain "
        "(o \"jeito\" da pessoa se cancela). Só pares em que a pessoa não empatou e vistos por 2+ "
        "participantes.\n\n"
        "- `correlacao`: Pearson entre a diferença humana e a do previsor (empate do previsor = 0); "
        "IC 95% por bootstrap de participantes.\n"
        "- `acordo`: quando o previsor escolhe um lado, quantas vezes é o mesmo da pessoa (acaso = 50%).\n"
        "- `empate`: quantas vezes o previsor dá a mesma nota aos dois (não escolhe).\n"
        "- `outro_humano`: média das diferenças dos outros participantes no mesmo par.\n"
        "A preferência da LLM vem de duas notas pedidas separadamente.\n\n",
        "## Média das 8 métricas (%)\n\n", media.round(1).to_markdown(),
        "\n\n## Correlação por métrica (%)\n\n", por_metrica.round(1).to_markdown(), "\n",
    ]
    (saida / "resumo.md").write_text("".join(texto), encoding="utf-8")
    print(media.round(1).to_string())
    print(f"\nResumo em {saida / 'resumo.md'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "configs" / "dave" / "mock.yaml"))
