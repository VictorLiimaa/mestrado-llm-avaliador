"""Baixa os dados de Lu et al. (2023) do repositório de Zhang et al. (2024) para dados/lu/.

Uso:  python scripts/dados_baixar_lu.py
Confere o MD5 de cada arquivo, para garantir que são exatamente os usados nos experimentos.
"""
import hashlib
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM = "https://raw.githubusercontent.com/Xiaoyu-SZ/LLMasEvaluator/main/data/"
ARQUIVOS = {
    "df_explanation.pkl": "f591acefe5ec14ab22b61c25a69cb35e",
    "third_party.csv": "a0f91b3495838d0a0e2f26cbe9146533",
    "df_explanation_selected.csv": "9141161ad613db8c30e494571f41dcf1",
    "user_demo.csv": "a77062082445dc32d422e491bf3d264f",
}


def md5(caminho: Path) -> str:
    return hashlib.md5(caminho.read_bytes()).hexdigest()


def main():
    destino = RAIZ / "dados" / "lu"
    destino.mkdir(parents=True, exist_ok=True)
    for nome, esperado in ARQUIVOS.items():
        caminho = destino / nome
        if not (caminho.exists() and md5(caminho) == esperado):
            print(f"Baixando {nome}...")
            urllib.request.urlretrieve(ORIGEM + nome, caminho)
        if md5(caminho) != esperado:
            raise SystemExit(f"{nome}: o arquivo baixado é diferente do esperado (MD5 não confere).")
        print(f"  {nome}: ok")
    print(f"Dados do Lu prontos em {destino}")


if __name__ == "__main__":
    main()
