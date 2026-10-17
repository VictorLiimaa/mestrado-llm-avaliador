"""Roda o usuário simulado / juiz LLM em cada modelo e condição de enriquecimento da configuração.

Uso:  python scripts/lu_02_rodar_juiz.py configs/lu/mock.yaml
As respostas ficam em resultados/<experimento>/cache/<modelo>__<condicao>.jsonl.
Se for interrompido, rodar de novo continua de onde parou.
"""
import sys
from pathlib import Path

import yaml

from avaliador.comum.llm import ConfigModelo, criar_llm
from avaliador.lu.dados import carregar
from avaliador.lu.juiz import amostrar_usuarios, avaliar

RAIZ = Path(__file__).resolve().parents[1]


def main(caminho_config: str):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    df = carregar(RAIZ / "dados" / "lu")
    alvo = amostrar_usuarios(df, cfg.get("n_usuarios"), cfg.get("semente", 2026))
    print(f"{alvo['user'].nunique()} usuários, {len(alvo)} explicações")

    pasta = RAIZ / "resultados" / cfg["experimento"] / "cache"
    for m in cfg["modelos"]:
        llm = criar_llm(ConfigModelo(**m))
        for condicao in cfg["condicoes"]:
            resultado = avaliar(df, alvo, llm, condicao, pasta / f"{llm.config.nome}__{condicao}.jsonl",
                                reproduzir_bug_transparencia=cfg.get("reproduzir_bug_transparencia", False),
                                resposta_curta=cfg.get("resposta_curta", False),
                                paralelo=cfg.get("paralelo", 1))
            falhas = resultado[f"{llm.config.nome}__{condicao}_falha"].mean()
            print(f"  {llm.config.nome} {condicao}: {100 * falhas:.1f}% de respostas que não puderam ser lidas")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "configs" / "lu" / "mock.yaml"))
