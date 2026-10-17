"""Dave, passo 1: reproduz as tabelas do teste com usuários a partir dos dados brutos.

Confere que estamos lendo os dados do jeito certo antes de colocar qualquer LLM no meio.
Uso:  python scripts/dave_01_reproduzir_teste.py
Saída: resultados/dave_artigo/tabelas_artigo.md
"""
from pathlib import Path

from avaliador.dave.avaliacao import formatar_tabela_artigo, tabela_artigo
from avaliador.dave.dados import carregar

RAIZ = Path(__file__).resolve().parents[1]

segues, notas = carregar(RAIZ / "dados" / "dave")
print(f"{notas['usuario'].nunique()} participantes com notas, {len(notas)} avaliações, "
      f"{segues['segue_idx'].nunique()} pares de segues")

tabela = formatar_tabela_artigo(tabela_artigo(notas))
pasta = RAIZ / "resultados" / "dave_artigo"
pasta.mkdir(parents=True, exist_ok=True)
with open(pasta / "tabelas_artigo.md", "w", encoding="utf-8") as f:
    f.write("# Reprodução das tabelas do teste do Dave (Gabbolini & Bridge, 2021)\n\n"
            "Médias de 1 a 5. Estrelas no vencedor: * p<0,05; ** p<0,01; *** p<0,001.\n"
            "Geral: teste t pareado. Informativos e engraçados: teste t independente "
            "(como no notebook dos autores).\n\n")
    for grupo in ["geral", "informativos", "engracados"]:
        t = tabela[tabela.grupo == grupo].set_index("metrica")[["dave", "the_chain"]].T
        f.write(f"## {grupo}\n\n{t.to_markdown()}\n\n")
        print(f"\n{grupo}\n{t.to_string()}")
print(f"\nSalvo em {pasta / 'tabelas_artigo.md'}")
