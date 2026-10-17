"""Meta-avaliação: correlação de cada modelo, condição de enriquecimento e combinação com as notas reais.

Uso:  python scripts/lu_03_avaliar.py configs/lu/mock.yaml
Saída: resultados/<experimento>/tabela_pearson.csv, tabela_spearman.csv, tabela_kendall.csv e resumo.md
As linhas dos anotadores humanos, calculadas na mesma amostra, servem de referência.
"""
import sys
from pathlib import Path

import pandas as pd
import yaml

from avaliador.lu.baselines import media_do_tipo
from avaliador.lu.dados import ASPECTOS, carregar
from avaliador.lu.juiz import amostrar_usuarios, combinar, juntar_notas, ler_cache
from avaliador.lu.metaavaliacao import bootstrap_usuarios, dentro_do_tipo, tabela

RAIZ = Path(__file__).resolve().parents[1]


def main(caminho_config: str):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    df = carregar(RAIZ / "dados" / "lu")
    alvo = amostrar_usuarios(df, cfg.get("n_usuarios"), cfg.get("semente", 2026))
    pasta = RAIZ / "resultados" / cfg["experimento"]

    # Baseline ingênuo calculado no conjunto completo (média do tipo pelos outros usuários).
    alvo = alvo.merge(media_do_tipo(df)[["row_id"] + [f"tipo_{a}" for a in ASPECTOS]], on="row_id")
    avaliadores = {"Annotator-1": "anot1", "Annotator-2": "anot2", "Media-do-tipo": "tipo"}
    n_referencias = len(avaliadores)
    falhas = []
    for m in cfg["modelos"]:
        for condicao in cfg["condicoes"]:
            arquivo = pasta / "cache" / f"{m['nome']}__{condicao}.jsonl"
            if not arquivo.exists():
                print(f"Sem resultados para {m['nome']} {condicao}; rode antes o lu_02_rodar_juiz.py.")
                continue
            prefixo = f"{m['nome']}__{condicao}"
            alvo = juntar_notas(alvo, ler_cache(arquivo), prefixo)
            avaliadores[f"{m['nome']} {condicao}"] = prefixo
            falhas.append({"modelo": m["nome"], "condicao": condicao,
                           "falhas_leitura_%": round(100 * alvo[f"{prefixo}_falha"].mean(), 2)})

    for comb in cfg.get("combinacao", []) or []:
        for condicao in cfg["condicoes"]:
            prefixos = [f"{nome}__{condicao}" for nome in comb["modelos"]]
            if all(f"{p}_{ASPECTOS[0]}" in alvo for p in prefixos):
                nome = f"{comb['nome']}__{condicao}"
                alvo = combinar(alvo, prefixos, nome)
                avaliadores[f"{comb['nome']} {condicao}"] = nome

    if len(avaliadores) == n_referencias:
        print("\nNenhum resultado de LLM encontrado. Rode antes: python scripts/lu_02_rodar_juiz.py " + caminho_config)
        return

    pasta.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.width", 250)
    with open(pasta / "resumo.md", "w", encoding="utf-8") as f:
        f.write(f"# Meta-avaliação: {cfg['experimento']}\n\n")
        f.write(f"{alvo['user'].nunique()} usuários, {len(alvo)} explicações. Valores em %.\n\n")
        for metodo in ["pearson", "spearman", "kendall"]:
            t = tabela(alvo, avaliadores, ASPECTOS, metodo).round(2)
            t.to_csv(pasta / f"tabela_{metodo}.csv")
            f.write(f"## {metodo.capitalize()}\n\n" + t.to_markdown() + "\n\n")
            if metodo == "pearson":
                print(t[[(a, "dataset") for a in ASPECTOS + ["average"]]])
        # Intervalos de confiança: cada condição do mesmo modelo comparada ao seu E0.
        referencia = {}
        for m in cfg["modelos"] + [{"nome": c["nome"]} for c in (cfg.get("combinacao") or [])]:
            base = f"{m['nome']} E0"
            if base in avaliadores:
                for condicao in cfg["condicoes"]:
                    nome = f"{m['nome']} {condicao}"
                    if condicao != "E0" and nome in avaliadores:
                        # foco_X é comparado com so_X (mesmo perfil, sem a instrução de foco);
                        # foco_E0 e as demais condições são comparadas com o E0.
                        par = f"{m['nome']} so_{condicao[5:]}" if condicao.startswith("foco_") else None
                        referencia[nome] = par if par in avaliadores else base
        primeiro_e0 = f"{cfg['modelos'][0]['nome']} E0"
        if primeiro_e0 in avaliadores:
            referencia["Media-do-tipo"] = primeiro_e0
        ic = bootstrap_usuarios(alvo, avaliadores, ASPECTOS, referencia,
                                reamostragens=cfg.get("reamostragens_bootstrap", 1000))
        ic.round(2).to_csv(pasta / "intervalos_confianca.csv")
        f.write("## Intervalos de confiança de 95% (bootstrap por usuário)\n\n"
                "Pearson médio nos 4 aspectos, nível conjunto. Na comparação com o E0, "
                "se o intervalo da diferença não contém zero, a diferença dificilmente é acaso.\n\n"
                + ic.round(2).to_markdown() + "\n\n")
        dt = dentro_do_tipo(alvo, {k: v for k, v in avaliadores.items() if k != "Media-do-tipo"}, ASPECTOS)
        dt.round(2).to_csv(pasta / "dentro_do_tipo.csv")
        f.write("## Correlação dentro do tipo de explicação\n\n"
                "Pearson médio calculado separadamente em cada um dos 9 tipos de explicação. Mede se o "
                "avaliador distingue explicações do mesmo tipo, e não só qual tipo costuma ser melhor.\n\n"
                + dt.round(2).to_markdown() + "\n\n")
        print("\nIntervalos de confiança (95%):")
        print(ic.round(2))
        if falhas:
            f.write("## Respostas que não puderam ser lidas\n\n" + pd.DataFrame(falhas).to_markdown(index=False) + "\n")
    print(f"\nResumo em {pasta / 'resumo.md'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "configs" / "lu" / "mock.yaml"))
