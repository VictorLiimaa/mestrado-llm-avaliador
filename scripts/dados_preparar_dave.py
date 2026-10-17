"""Copia para dados/dave/ os arquivos do teste com usuários do Dave publicados no Zenodo.

1. Baixe o arquivo em https://doi.org/10.5281/zenodo.4618570 e descompacte.
2. Rode, apontando para a pasta `res` descompactada (ou para o .zip):
       python scripts/dados_preparar_dave.py caminho/para/res
       python scripts/dados_preparar_dave.py caminho/para/arquivo.zip

Só são copiados os arquivos usados nos experimentos. O comments.json NÃO é copiado: tem
comentários livres dos participantes, e um deles traz dados de contato.
"""
import hashlib
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "dados" / "dave"
MD5 = {
    "answers.json": "7fd649c5f3a50097a931cd705bece8ca",
    "df_segue_category_dave.csv": "bdeb1a3d4424ea1fcc6cb3726d8cf3a3",
    "df_segue_category_the_chain.csv": "2cc6c6ed2e566bc39d0d9d21595c4609",
}
N_PARES = 200


def achar_pasta_p(origem: Path) -> Path:
    """Procura a pasta res/p (pode estar aninhada, como em res/res/p)."""
    for candidata in [origem, *origem.rglob("p")]:
        if (candidata / "answers" / "answers.json").exists():
            return candidata
    raise SystemExit(f"Não encontrei answers/answers.json dentro de {origem}.")


def copiar(pasta_p: Path) -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, esperado in MD5.items():
        alvo = DESTINO / nome
        shutil.copyfile(pasta_p / "answers" / nome, alvo)
        if hashlib.md5(alvo.read_bytes()).hexdigest() != esperado:
            raise SystemExit(f"{nome}: diferente do arquivo usado nos experimentos (MD5 não confere).")
        print(f"  {nome}: ok")
    pares = sorted((pasta_p / "user_trial_sample").glob("*.json"))
    if len(pares) != N_PARES:
        raise SystemExit(f"Esperava {N_PARES} arquivos em user_trial_sample, achei {len(pares)}.")
    (DESTINO / "user_trial_sample").mkdir(exist_ok=True)
    for arquivo in pares:
        shutil.copyfile(arquivo, DESTINO / "user_trial_sample" / arquivo.name)
    print(f"  user_trial_sample: {len(pares)} arquivos")


def main(origem: str):
    origem = Path(origem)
    if origem.suffix == ".zip":
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(origem) as z:
                membros = [m for m in z.namelist()
                           if "/answers/" in m or "/user_trial_sample/" in m]
                z.extractall(tmp, members=membros)
            copiar(achar_pasta_p(Path(tmp)))
    else:
        copiar(achar_pasta_p(origem))
    print(f"Dados do Dave prontos em {DESTINO}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
