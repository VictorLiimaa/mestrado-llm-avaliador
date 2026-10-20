"""Dave, passo 4: teste offline de treino e teste. A LLM prevê as notas de cada participante.

Para cada participante e cada par que ele avaliou, esse par é o teste. Conforme a condição, o
prompt traz informação sobre o participante: as notas dele nos outros pares (`historico`), as
respostas sobre si (`perfil`), se conhecia as músicas (`familiaridade`) ou combinações; a lista
de condições vem de `treino_teste.condicoes` na configuração (padrão: só `historico`).
Compara com previsores sem LLM (média do próprio participante, média dos outros participantes,
soma dos dois) e com o E0, se existir. Detalhes em src/avaliador/dave/treino_teste.py.

Uso:  python scripts/dave_04_treino_teste.py configs/dave/local.yaml
      python scripts/dave_04_treino_teste.py configs/dave/local.yaml --so-avaliar   (sem chamar a LLM)
Saída: resultados/<experimento>/treino_teste/resumo.md, comparacao.csv e graficos/*.png.
As respostas ficam em resultados/<experimento>/cache/<modelo>__<condicao>.jsonl.
São cerca de 900 chamadas por modelo e condição; se for interrompido, continua de onde parou.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from avaliador.comum.llm import ConfigModelo, criar_llm
from avaliador.dave import juiz, treino_teste
from avaliador.dave.dados import METRICAS, carregar, carregar_familiaridade, carregar_perfis

RAIZ = Path(__file__).resolve().parents[1]


def _media_dos_modelos(tabelas: list[pd.DataFrame]) -> pd.DataFrame:
    media = tabelas[0].copy()
    media[METRICAS] = np.mean([t[METRICAS].to_numpy(float) for t in tabelas], axis=0)
    media["falha"] = np.any([t["falha"] for t in tabelas], axis=0)
    return media


def main(caminho_config: str, so_avaliar: bool = False):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    segues, notas = carregar(RAIZ / "dados" / "dave")
    pasta = RAIZ / "resultados" / cfg["experimento"]
    cache = pasta / "cache"
    saida = pasta / "treino_teste"
    saida.mkdir(parents=True, exist_ok=True)
    print(f"{notas['usuario'].nunique()} participantes, {len(notas)} notas para prever")

    previsores = treino_teste.previsores_sem_llm(notas)
    condicoes = (cfg.get("treino_teste") or {}).get("condicoes", ["historico"])
    perfis = carregar_perfis(RAIZ / "dados" / "dave")
    familiaridade = carregar_familiaridade(RAIZ / "dados" / "dave")
    falhas = {}
    por_condicao = {"E0": {}, **{c: {} for c in condicoes}}
    for m in cfg["modelos"]:
        nome = m["nome"]
        llm = None if so_avaliar else criar_llm(ConfigModelo(**m))
        for condicao in condicoes:
            arquivo = cache / f"{nome}__{condicao}.jsonl"
            if llm is not None:
                treino_teste.avaliar(notas, segues, llm, arquivo, condicao, perfis, familiaridade,
                                     cfg.get("resposta_curta", True), cfg.get("paralelo", 1))
            if arquivo.exists():
                t = treino_teste.tabela_notas(notas, treino_teste.ler_cache(arquivo))
                por_condicao[condicao][nome] = t
                falhas[f"{nome}__{condicao}"] = t["falha"].mean()
            else:
                print(f"Sem respostas de {nome} em {condicao}; rode sem --so-avaliar.")
        arquivo_e0 = cache / f"{nome}__E0.jsonl"
        if arquivo_e0.exists():
            por_condicao["E0"][nome] = juiz.tabela_notas(segues, juiz.ler_cache(arquivo_e0))
        else:
            print(f"Sem o E0 de {nome}; para comparar, rode antes o dave_02_rodar_juiz.py.")

    for condicao, tabelas in por_condicao.items():
        for nome, t in tabelas.items():
            previsores[f"{nome}__{condicao}"] = t.drop(columns="falha")
        for comb in cfg.get("combinacao", []) or []:
            partes = [tabelas.get(n) for n in comb["modelos"]]
            if all(p is not None for p in partes):
                previsores[f"{comb['nome']}__{condicao}"] = _media_dos_modelos(partes).drop(columns="falha")

    tabela = treino_teste.comparar(notas, previsores, "media_usuario",
                                   cfg.get("reamostragens_bootstrap", 1000))
    tabela.round(4).to_csv(saida / "comparacao.csv", index=False)

    media = tabela[tabela["metrica"] == treino_teste.MEDIA].set_index("previsor")
    principal = media[["pearson_%", "ic_inf_%", "ic_sup_%", "centrada_%", "centrada_ic_inf_%",
                       "centrada_ic_sup_%", "dif_vs_media_usuario_%", "dif_ic_inf_%", "dif_ic_sup_%"]]
    por_metrica = tabela.pivot(index="metrica", columns="previsor", values="pearson_%")
    por_metrica_c = tabela.pivot(index="metrica", columns="previsor", values="centrada_%")
    n = int(tabela.loc[tabela["metrica"] != treino_teste.MEDIA, "n"].min())

    partes = [
        f"# Treino e teste no Dave: {cfg['experimento']}\n",
        f"{notas['usuario'].nunique()} participantes. Cada par avaliado vira teste uma vez; o treino "
        f"são os outros pares do mesmo participante. Comparação em pelo menos {n} notas por métrica "
        "(segues vistos por 2+ participantes, sem falha de leitura).\n",
        "- `pearson`: correlação com a nota do participante.\n"
        "- `centrada`: correlação dentro do participante (a média de cada participante sai da nota "
        "real e da previsão): só a reação ao segue, sem o \"jeito\" da pessoa. A `media_usuario` "
        "sai negativa aqui por construção: ela não sabe nada sobre os segues.\n"
        "- `dif_vs_media_usuario`: diferença de Pearson para a média do próprio participante; "
        "se o IC não inclui zero, a diferença é significativa a 5%.\n"
        "- IC 95% por bootstrap de participantes.\n",
    ]
    if falhas:
        partes.append("Respostas que não puderam ser lidas: " +
                      ", ".join(f"{k} {100 * v:.1f}%" for k, v in falhas.items()) + "\n")
    partes += [
        "\n## Média dos 8 critérios (%)\n\n", principal.round(1).to_markdown(),
        "\n\n## Pearson por critério (%)\n\n", por_metrica.round(1).to_markdown(),
        "\n\n## Pearson com a nota centrada, por critério (%)\n\n", por_metrica_c.round(1).to_markdown(), "\n",
        "\n## Sem LLM: conhecer as músicas muda a nota? (Pearson % dentro do participante)\n\n",
        treino_teste.efeito_familiaridade(notas, familiaridade).round(1).to_markdown(), "\n",
    ]
    try:
        from avaliador.dave.graficos import gerar
        imagens = gerar(tabela, saida / "graficos")
        partes.append("\n## Gráficos\n\n" + "\n".join(f"![{i.stem}](graficos/{i.name})" for i in imagens) + "\n")
    except ImportError:
        print("matplotlib não instalado: gráficos não gerados (python -m pip install matplotlib).")
    (saida / "resumo.md").write_text("".join(partes), encoding="utf-8")
    pd.set_option("display.width", 200)
    print(principal.round(1).to_string())
    print(f"\nResumo em {saida / 'resumo.md'}")


if __name__ == "__main__":
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(argumentos[0] if argumentos else str(RAIZ / "configs" / "dave" / "mock.yaml"),
         so_avaliar="--so-avaliar" in sys.argv)
