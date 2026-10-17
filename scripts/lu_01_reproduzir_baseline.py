"""Baseline do baseline: anotadores humanos e BLEU/ROUGE contra as notas reais dos usuários.

Reproduz as linhas não-LLM da Tabela 1 de Zhang et al. (2024) e compara com os valores publicados.
Uso:  python scripts/lu_01_reproduzir_baseline.py
Saída: resultados/lu_baseline/baseline_do_baseline.csv e .md
"""
from pathlib import Path

import pandas as pd

from avaliador.lu.baselines import calcular_metricas_referencia
from avaliador.lu.dados import ASPECTOS, carregar
from avaliador.lu.metaavaliacao import NIVEIS, tabela

RAIZ = Path(__file__).resolve().parents[1]

# Tabela 1 de Zhang et al. (2024): Pearson (%) conjunto / usuário / par, por aspecto.
PUBLICADO = {
    "BLEU-1": {"persuasiveness": (11.68, 15.84, 17.07), "transparency": (10.06, 12.69, 14.44),
               "accuracy": (6.43, 10.71, 12.18), "satisfaction": (11.36, 12.91, 15.79)},
    "BLEU-4": {"persuasiveness": (-1.17, 7.68, 13.53), "transparency": (-3.47, 4.13, 10.24),
               "accuracy": (-4.63, 4.8, 8.96), "satisfaction": (0.61, 6.86, 12.09)},
    "ROUGE-1-F": {"persuasiveness": (14.16, 16.39, 17.56), "transparency": (11.93, 12.74, 14.45),
                  "accuracy": (8.61, 11.02, 12.83), "satisfaction": (12.87, 13.2, 16.23)},
    "ROUGE-L-F": {"persuasiveness": (14.16, 16.39, 17.56), "transparency": (11.93, 12.74, 14.45),
                  "accuracy": (8.61, 11.02, 12.83), "satisfaction": (12.87, 13.2, 16.23)},
    "Annotator-1": {"persuasiveness": (19.88, 18.31, 16.72), "transparency": (15.66, 16.18, 11.31),
                    "accuracy": (10.16, 9.78, 9.77), "satisfaction": (14.93, 13.28, 12.69)},
    "Annotator-2": {"persuasiveness": (21.4, 21.17, 20.9), "transparency": (25.97, 26.42, 27.84),
                    "accuracy": (10.96, 10.96, 9.32), "satisfaction": (8.86, 9.72, 9.43)},
}
AVALIADORES = {"BLEU-1": "bleu1", "BLEU-4": "bleu4", "ROUGE-1-F": "rouge1f", "ROUGE-L-F": "rougelf",
               "Annotator-1": "anot1", "Annotator-2": "anot2"}


def main():
    df = calcular_metricas_referencia(carregar(RAIZ / "dados" / "lu"))
    nosso = tabela(df, AVALIADORES, ASPECTOS)

    linhas = []
    for avaliador in AVALIADORES:
        for aspecto in ASPECTOS:
            for i, nivel in enumerate(NIVEIS):
                reproduzido = nosso.loc[avaliador, (aspecto, nivel)]
                publicado = PUBLICADO[avaliador][aspecto][i]
                linhas.append({"avaliador": avaliador, "aspecto": aspecto, "nivel": nivel,
                               "reproduzido": round(reproduzido, 2), "publicado": publicado,
                               "diferenca": round(reproduzido - publicado, 2)})
    comparacao = pd.DataFrame(linhas)

    saida = RAIZ / "resultados" / "lu_baseline"
    saida.mkdir(parents=True, exist_ok=True)
    comparacao.to_csv(saida / "baseline_do_baseline.csv", index=False)

    resumo = comparacao.groupby("avaliador", sort=False)["diferenca"].agg(
        dif_media_abs=lambda s: s.abs().mean(), dif_max_abs=lambda s: s.abs().max())
    with open(saida / "baseline_do_baseline.md", "w", encoding="utf-8") as f:
        f.write("# Baseline do baseline: reprodução das linhas não-LLM da Tabela 1 (Zhang et al., 2024)\n\n")
        f.write("Pearson (%) entre o avaliador e as notas reais. Diferença = reproduzido - publicado.\n\n")
        f.write(resumo.round(2).to_markdown() + "\n\n")
        f.write(comparacao.to_markdown(index=False) + "\n")
    pd.set_option("display.width", 200)
    print(resumo.round(2))
    print(f"\nTabela completa em {saida / 'baseline_do_baseline.md'}")


if __name__ == "__main__":
    main()
