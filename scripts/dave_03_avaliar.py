"""Dave, passo 3: compara o ouvinte simulado (LLM) com os 151 participantes reais.

Uso:  python scripts/dave_03_avaliar.py configs/dave/local.yaml
Saída: resultados/<experimento>/resumo.md (+ CSVs)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from avaliador.dave.avaliacao import conclusoes, correlacoes, escolha_no_par
from avaliador.dave.dados import METRICAS, carregar
from avaliador.dave.juiz import ler_cache, tabela_notas

RAIZ = Path(__file__).resolve().parents[1]


def main(caminho_config: str):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    segues, notas = carregar(RAIZ / "dados" / "dave")
    pasta = RAIZ / "resultados" / cfg["experimento"]
    pasta.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 200)

    partes = [f"# Ouvinte simulado no teste do Dave: {cfg['experimento']}\n",
              f"{notas['usuario'].nunique()} participantes, {len(notas)} avaliações, "
              f"{len(segues)} segues.\n"]
    # Referência de acaso: notas sorteadas de 1 a 5. Mostra quantas "conclusões iguais" e quanta
    # correlação aparecem sem nenhuma inteligência (ex.: "nenhum dos dois é significativo" conta
    # como concordância e acontece muito por acaso).
    rng = np.random.default_rng(2026)
    iguais, acordos = [], []
    for _ in range(cfg.get("sorteios_acaso", 20)):
        aleatorio = segues[["segue_idx", "sistema"]].copy()
        for met in METRICAS:
            aleatorio[met] = rng.integers(1, 6, len(aleatorio))
        iguais.append(conclusoes(notas, segues, aleatorio)["mesma_conclusao"].sum())
        acordos.append(escolha_no_par(notas, aleatorio)["acordo_%"].mean())
    partes.append(f"\n**Referência de acaso** (notas sorteadas, {len(iguais)} sorteios): mesma conclusão "
                  f"em {np.mean(iguais):.1f} de 24 em média (mín. {min(iguais)}, máx. {max(iguais)}); "
                  f"acordo no par {np.mean(acordos):.1f}%.\n")
    print(partes[-1].strip())

    # Notas de cada modelo e condição (e das combinações, pela média dos modelos).
    avaliadores = {}
    for m in cfg["modelos"]:
        for condicao in cfg["condicoes"]:
            arquivo = pasta / "cache" / f"{m['nome']}__{condicao}.jsonl"
            if not arquivo.exists():
                print(f"Sem resultados para {m['nome']} {condicao}; rode antes o dave_02_rodar_juiz.py.")
                continue
            avaliadores[(m["nome"], condicao)] = tabela_notas(segues, ler_cache(arquivo))
    for comb in cfg.get("combinacao", []) or []:
        for condicao in cfg["condicoes"]:
            partes_comb = [avaliadores.get((nome, condicao)) for nome in comb["modelos"]]
            if all(p is not None for p in partes_comb):
                media = partes_comb[0].copy()
                media[METRICAS] = np.mean([p[METRICAS].to_numpy(float) for p in partes_comb], axis=0)
                media["falha"] = np.any([p["falha"] for p in partes_comb], axis=0)
                avaliadores[(comb["nome"], condicao)] = media
    algum = bool(avaliadores)

    for (modelo, condicao), llm in avaliadores.items():
        nome = f"{modelo}__{condicao}"
        notas_llm = llm.drop(columns="falha")
        conc = conclusoes(notas, segues, notas_llm)
        corr = correlacoes(notas, notas_llm, cfg.get("reamostragens_bootstrap", 1000))
        par = escolha_no_par(notas, notas_llm)
        for df, sufixo in [(conc, "conclusoes"), (corr, "correlacoes"), (par, "escolha_no_par")]:
            df.round(4).to_csv(pasta / f"{nome}__{sufixo}.csv", index=False)

        n_iguais = int(conc["mesma_conclusao"].sum())
        corr_w = corr.pivot(index="metrica", columns="avaliador", values="pearson_%")
        partes += [
            f"\n## {modelo} — {condicao}\n",
            f"Respostas que não puderam ser lidas: {100 * llm['falha'].mean():.1f}%\n",
            f"\n### 1. Conclusões (Dave − The Chain, no nível do segue)\n\n"
            f"Mesma conclusão que os humanos em **{n_iguais} de {len(conc)}** comparações "
            "(mesma significância a 5% e, se significativa, mesmo sentido).\n\n",
            conc.round(3).to_markdown(index=False),
            "\n\n### 2. Correlação com cada participante (Pearson %, p-valor e IC 95%)\n\n"
            "`outro_humano` = média dos outros participantes que viram o mesmo segue "
            "(o quanto as pessoas concordam entre si). `ic_fisher` = intervalo do "
            "scipy.stats.pearsonr (supõe notas independentes); `ic_boot` = bootstrap por "
            "participante (respeita as várias notas de cada pessoa).\n\n",
            corr.round(2).to_markdown(index=False),
            f"\n\nMédia nas 8 métricas: LLM {corr_w['llm'].mean():.2f}% | "
            f"outro humano {corr_w['outro_humano'].mean():.2f}%\n",
            "\n### 3. Escolha no par (acordo com o participante; acaso = 50%)\n\n",
            par.round(2).to_markdown(index=False), "\n",
        ]
        print(f"\n{nome}: mesma conclusão em {n_iguais}/{len(conc)}; "
              f"Pearson médio LLM {corr_w['llm'].mean():.2f}% vs outro humano "
              f"{corr_w['outro_humano'].mean():.2f}%; acordo no par {par['acordo_%'].mean():.1f}%")
    if not algum:
        print("\nNenhum resultado encontrado. Rode antes: python scripts/dave_02_rodar_juiz.py " + caminho_config)
        return
    (pasta / "resumo.md").write_text("\n".join(partes), encoding="utf-8")
    print(f"\nResumo em {pasta / 'resumo.md'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "configs" / "dave" / "mock.yaml"))
