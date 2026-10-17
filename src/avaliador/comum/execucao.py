"""Execução de uma LLM sobre uma lista de itens, com cache em JSONL.

Cada resposta é gravada numa linha do arquivo assim que chega. Se a execução for interrompida,
rodar de novo pula o que já está no arquivo e continua de onde parou.
"""
from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Iterable

from .llm import LLM, ler_notas


def ler_cache(arquivo: str | Path, campo_chave: str) -> dict:
    """Registros já gravados, indexados pelo campo que identifica o item."""
    arquivo = Path(arquivo)
    if not arquivo.exists():
        return {}
    registros = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            registro = json.loads(linha)
            registros[registro[campo_chave]] = registro
    return registros


def executar(
    itens: Iterable,
    chave: Callable,
    montar_prompt: Callable,
    llm: LLM,
    arquivo: str | Path,
    campo_chave: str,
    n_notas: int,
    condicao: str,
    paralelo: int = 1,
    progresso: bool = True,
) -> dict:
    """Pede à LLM as notas de cada item que ainda não está no cache.

    `chave(item)` identifica o item no cache; `montar_prompt(item)` devolve o texto enviado.
    Devolve todos os registros (antigos e novos), indexados pela chave.
    """
    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    feitos = ler_cache(arquivo, campo_chave)
    pendentes = [item for item in itens if chave(item) not in feitos]

    barra = None
    if progresso and pendentes:
        try:
            from tqdm import tqdm

            barra = tqdm(total=len(pendentes), desc=f"{llm.config.nome} {condicao}")
        except ImportError:
            pass
    trava = threading.Lock()

    def processar(item) -> dict:
        resposta = llm.gerar(montar_prompt(item))
        return {campo_chave: chave(item), "modelo": llm.config.nome, "condicao": condicao,
                "resposta": resposta, "notas": ler_notas(resposta, quantidade=n_notas)}

    with arquivo.open("a", encoding="utf-8") as saida:
        def gravar(registro: dict) -> None:
            with trava:
                saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
                saida.flush()
                feitos[registro[campo_chave]] = registro
                if barra:
                    barra.update(1)

        if paralelo <= 1:
            for item in pendentes:
                gravar(processar(item))
        else:
            with ThreadPoolExecutor(max_workers=paralelo) as executor:
                for futuro in as_completed([executor.submit(processar, i) for i in pendentes]):
                    gravar(futuro.result())
    if barra:
        barra.close()
    return feitos
