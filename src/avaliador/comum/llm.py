"""Camada de acesso a LLMs e leitura das respostas.

Backends:
- "mock": modelo falso e determinístico, para testar o pipeline sem GPU nem custo.
- "openai_compat": qualquer servidor com a API de chat do OpenAI. Serve para OpenAI, OpenRouter,
  um servidor vLLM local (`vllm serve <modelo>`) ou Ollama (`http://localhost:11434/v1`).
  Usa só a biblioteca padrão do Python (urllib), sem dependências extras.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

_NOTA = re.compile(r"(?<!\d)[1-5](?!\d)")


def ler_notas(resposta: str, quantidade: int = 4) -> list[int] | None:
    """Pega as últimas `quantidade` notas de 1 a 5 da resposta. Devolve None se não houver o suficiente.

    Zhang et al. pedem que a resposta termine com as notas ("3 3 3 3"), então olhamos o final.
    """
    if not isinstance(resposta, str):
        return None
    notas = [int(n) for n in _NOTA.findall(resposta)]
    if len(notas) < quantidade:
        return None
    return notas[-quantidade:]


@dataclass
class ConfigModelo:
    nome: str                      # nome usado nos resultados, ex.: "qwen2.5-7b"
    backend: str                   # "mock" ou "openai_compat"
    modelo: str = ""               # nome do modelo no servidor
    base_url: str = "https://api.openai.com/v1"
    api_key_env: str = "OPENAI_API_KEY"
    temperatura: float = 0.0
    max_tokens: int = 256
    tentativas: int = 3
    extra: dict = field(default_factory=dict)


class LLM:
    def __init__(self, config: ConfigModelo):
        self.config = config

    def gerar(self, prompt: str) -> str:
        raise NotImplementedError


class MockLLM(LLM):
    """Devolve notas pseudoaleatórias estáveis (mesmo prompt, mesma resposta). Só para testes."""

    def gerar(self, prompt: str) -> str:
        semente = int(hashlib.sha256((self.config.nome + prompt).encode()).hexdigest(), 16)
        notas = [(semente >> (8 * i)) % 5 + 1 for i in range(8)]  # 8 serve ao Lu (lê as 4 últimas) e ao Dave
        return "Ratings: " + " ".join(map(str, notas))


class OpenAICompatLLM(LLM):
    def gerar(self, prompt: str) -> str:
        chave = os.environ.get(self.config.api_key_env, "")
        corpo = {
            "model": self.config.modelo,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperatura,
            "max_tokens": self.config.max_tokens,
            **self.config.extra,
        }
        pedido = urllib.request.Request(
            self.config.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(corpo).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {chave}"},
        )
        erro = None
        for tentativa in range(self.config.tentativas):
            try:
                with urllib.request.urlopen(pedido, timeout=120) as resposta:
                    dados = json.loads(resposta.read())
                return dados["choices"][0]["message"]["content"]
            except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
                erro = e
                time.sleep(2 ** tentativa)
        raise RuntimeError(f"Falha ao chamar {self.config.nome}: {erro}")


def criar_llm(config: ConfigModelo) -> LLM:
    if config.backend == "mock":
        return MockLLM(config)
    if config.backend == "openai_compat":
        return OpenAICompatLLM(config)
    raise ValueError(f"Backend desconhecido: {config.backend}")
