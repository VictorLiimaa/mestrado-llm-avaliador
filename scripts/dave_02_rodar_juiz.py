"""Dave, passo 2: a LLM avalia cada segue do teste, como se fosse um participante.

São 344 segues (172 pares x 2 sistemas) por modelo e condição: roda em poucos minutos.
Uso:  python scripts/dave_02_rodar_juiz.py configs/dave/local.yaml
As respostas ficam em resultados/<experimento>/cache/<modelo>__<condicao>.jsonl.
"""
import sys
from pathlib import Path

import yaml

from avaliador.comum.llm import ConfigModelo, criar_llm
from avaliador.dave.dados import carregar
from avaliador.dave.juiz import avaliar, tabela_notas

RAIZ = Path(__file__).resolve().parents[1]


def main(caminho_config: str):
    cfg = yaml.safe_load(Path(caminho_config).read_text(encoding="utf-8"))
    segues, _ = carregar(RAIZ / "dados" / "dave")
    print(f"{len(segues)} segues para avaliar")
    pasta = RAIZ / "resultados" / cfg["experimento"] / "cache"
    for m in cfg["modelos"]:
        llm = criar_llm(ConfigModelo(**m))
        for condicao in cfg["condicoes"]:
            registros = avaliar(segues, llm, condicao, pasta / f"{llm.config.nome}__{condicao}.jsonl",
                                resposta_curta=cfg.get("resposta_curta", True),
                                paralelo=cfg.get("paralelo", 1))
            falhas = tabela_notas(segues, registros)["falha"].mean()
            print(f"  {llm.config.nome} {condicao}: {100 * falhas:.1f}% de respostas que não puderam ser lidas")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "configs" / "dave" / "mock.yaml"))
