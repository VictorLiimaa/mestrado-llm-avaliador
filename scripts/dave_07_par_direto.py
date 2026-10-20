"""Dave, passo 7: comparação direta no par ("separar os papéis").

A LLM vê os dois segues de um par lado a lado e diz, por afirmação, qual descreve melhor para a
pessoa (A ou B); cada par é perguntado nas duas ordens. O "jeito" da pessoa não entra; só a
preferência. Compara com outro participante e com a preferência derivada das notas separadas
(E0 do passo 2). Detalhes em src/avaliador/dave/par_direto.py.

Uso:  python scripts/dave_07_par_direto.py configs/dave/local.yaml
      python scripts/dave_07_par_direto.py configs/dave/local.yaml --so-avaliar   (sem chamar a LLM)
As condições vêm de `par_direto.condicoes` na configuração (padrão: E0, perfil, familiaridade).
Respostas em resultados/<experimento>/cache/<modelo>__par2_<condicao>.jsonl. ("par2": a primeira
versão do prompt trazia um exemplo de resposta que o Qwen copiou em 83-92% dos pares; os arquivos
"__par_" dessa versão não são usados.)
Chamadas por modelo: 344 no E0 e cerca de 900 em cada outra condição.
Saída: resultados/<experimento>/par_direto/resumo.md, comparacao.csv, consistencia.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from avaliador.comum.llm import ConfigModelo, criar_llm
from avaliador.dave import escolha_par, juiz, par_direto
from avaliador.dave.dados import METRICAS, carregar, carregar_familiaridade, carregar_perfis

RAIZ = Path(__file__).resolve().parents[1]


def main(caminho_config: str, so_avaliar: bool = False):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    pasta_dados = RAIZ / "dados" / "dave"
    segues, notas = carregar(pasta_dados)
    perfis, familiaridade = carregar_perfis(pasta_dados), carregar_familiaridade(pasta_dados)
    pasta = RAIZ / "resultados" / cfg["experimento"]
    condicoes = (cfg.get("par_direto") or {}).get("condicoes", ["E0", "perfil", "familiaridade"])

    previsores, tabelas, consist = {}, {}, []
    for m in cfg["modelos"]:
        llm = None if so_avaliar else criar_llm(ConfigModelo(**m))
        for condicao in condicoes:
            arquivo = pasta / "cache" / f"{m['nome']}__par2_{condicao}.jsonl"
            if llm is not None:
                par_direto.avaliar(notas, segues, llm, arquivo, condicao, perfis, familiaridade,
                                   cfg.get("paralelo", 1))
            if not arquivo.exists():
                print(f"Sem respostas de {m['nome']} em par_{condicao}; rode sem --so-avaliar.")
                continue
            t, c = par_direto.preferencias(notas, par_direto.ler_cache(arquivo), condicao)
            tabelas[(m["nome"], condicao)] = t
            previsores[f"{m['nome']}__par_{condicao}"] = t
            consist.append(c.assign(previsor=f"{m['nome']}__par_{condicao}"))
        # referência: preferência derivada das notas separadas (E0 do passo 2)
        arquivo_e0 = pasta / "cache" / f"{m['nome']}__E0.jsonl"
        if arquivo_e0.exists():
            previsores[f"{m['nome']}__notas_E0"] = juiz.tabela_notas(segues, juiz.ler_cache(arquivo_e0)).drop(columns="falha")
    for comb in cfg.get("combinacao", []) or []:
        for condicao in condicoes:
            partes = [tabelas.get((n, condicao)) for n in comb["modelos"]]
            if all(p is not None for p in partes):
                media = partes[0].copy()
                media[METRICAS] = np.mean([p[METRICAS].to_numpy(float) for p in partes], axis=0)
                previsores[f"{comb['nome']}__par_{condicao}"] = media
    if not tabelas:
        print("Nenhuma resposta da comparação direta no cache.")
        return

    t = escolha_par.comparar(notas, previsores, cfg.get("reamostragens_bootstrap", 1000))
    consistencia = pd.concat(consist)
    saida = pasta / "par_direto"
    saida.mkdir(parents=True, exist_ok=True)
    t.round(4).to_csv(saida / "comparacao.csv", index=False)
    consistencia.round(2).to_csv(saida / "consistencia.csv", index=False)

    media = t[t["metrica"] == escolha_par.MEDIA].set_index("previsor").drop(columns=["metrica", "pares"])
    por_metrica = t[t["metrica"] != escolha_par.MEDIA].pivot(index="metrica", columns="previsor",
                                                             values="correlacao_%")
    resumo_c = consistencia.groupby("previsor")[["mesma_escolha_nas_duas_ordens_%", "falhas_%"]].mean()
    texto = [
        f"# Comparação direta no par: {cfg['experimento']}\n\n",
        "A LLM vê os dois segues de um par e diz qual descreve melhor cada afirmação para a pessoa; "
        "cada par nas duas ordens (Dave como A e como B). Preferência prevista: +1 Dave, −1 The Chain, "
        "0 quando as duas ordens se contradizem. Mesmas medidas da escolha no par (passo 6): "
        "`correlacao` (principal, IC 95% por bootstrap de participantes), `acordo` (acaso = 50%), "
        "`empate` (aqui: as duas ordens se contradisseram). `notas_E0` = preferência derivada das "
        "notas separadas do passo 2.\n\n",
        "## Média das 8 métricas (%)\n\n", media.round(1).to_markdown(),
        "\n\n## Correlação por métrica (%)\n\n", por_metrica.round(1).to_markdown(),
        "\n\n## Viés de posição: mesma escolha nas duas ordens (%)\n\n", resumo_c.round(1).to_markdown(), "\n",
    ]
    (saida / "resumo.md").write_text("".join(texto), encoding="utf-8")
    pd.set_option("display.width", 200)
    print(media.round(1).to_string())
    print(resumo_c.round(1).to_string())
    print(f"\nResumo em {saida / 'resumo.md'}")


if __name__ == "__main__":
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(argumentos[0] if argumentos else str(RAIZ / "configs" / "dave" / "mock.yaml"),
         so_avaliar="--so-avaliar" in sys.argv)
