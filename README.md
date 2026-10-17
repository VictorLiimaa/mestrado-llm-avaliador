# LLMs como usuários simulados para avaliar explicações de recomendação

Código dos experimentos do mestrado de Victor Oliveira Lima Pontes (ICMC/USP), sob orientação do
Prof. Marcelo Garcia Manzato.

**Pergunta:** uma LLM consegue fazer o papel de pessoas reais na avaliação de explicações de
recomendação? Testamos isso em dois conjuntos de dados com notas de pessoas reais:

| Experimento | Domínio | Dados | O que a LLM faz |
|---|---|---|---|
| **Lu** | Filmes (chinês) | Lu et al. (2023), via Zhang et al. (2024): 39 usuários, 2.536 explicações | Dá 4 notas (persuasão, transparência, precisão, satisfação) como se fosse o usuário |
| **Dave** | Música (inglês) | Teste com usuários de Gabbolini & Bridge (2021): 151 participantes, 172 pares de segues | Faz o teste no lugar dos participantes: mesma tela, mesmas 8 perguntas |

Em ambos, a LLM é comparada com as pessoas reais e com uma referência humana (anotadores externos
no Lu; a concordância entre participantes no Dave).

## Instalação

Requer Python 3.10 ou mais novo.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # instala o pacote `avaliador` em modo editável + pytest
```

Para rodar as LLMs localmente, instale o [Ollama](https://ollama.com) e baixe os modelos:

```bash
ollama pull qwen2.5:7b
ollama pull llama3.1:8b
```

O backend `openai_compat` também funciona com vLLM, OpenAI ou OpenRouter: basta trocar `base_url`
e `modelo` na configuração. A chave vai numa variável de ambiente (campo `api_key_env`), nunca no arquivo.

## Dados

Os dados não são redistribuídos aqui. Veja [`dados/README.md`](dados/README.md):

```bash
python scripts/dados_baixar_lu.py                                  # baixa e confere os dados do Lu
python scripts/dados_preparar_dave.py caminho/para/arquivo.zip     # zip do Zenodo do Dave
```

## Como reproduzir

Cada experimento tem três passos: reproduzir o artigo original (sem LLM), rodar a LLM e comparar
com as pessoas. O passo 2 grava as respostas em `resultados/<experimento>/cache/` e, se for
interrompido, continua de onde parou. As respostas das rodadas reais estão versionadas, então os
passos 1 e 3 rodam sem LLM.

### Lu (filmes)

```bash
python scripts/lu_01_reproduzir_baseline.py               # anotadores e BLEU/ROUGE vs. Tabela 1 de Zhang et al.
python scripts/lu_02_rodar_juiz.py configs/lu/qwen.yaml   # LLM (Ollama); ~2 h com todas as condições
python scripts/lu_03_avaliar.py configs/lu/qwen.yaml      # correlações em 3 níveis, IC 95%, análise dentro do tipo
```

`configs/lu/llama.yaml` faz o mesmo com o Llama.

### Dave (música)

```bash
python scripts/dave_01_reproduzir_teste.py                # tabelas do teste com usuários
python scripts/dave_02_rodar_juiz.py configs/dave/local.yaml   # Qwen e Llama; ~10 min
python scripts/dave_03_avaliar.py configs/dave/local.yaml      # conclusões, correlação, escolha no par
```

### Sem LLM (teste do pipeline)

```bash
python scripts/lu_02_rodar_juiz.py configs/lu/mock.yaml && python scripts/lu_03_avaliar.py configs/lu/mock.yaml
python scripts/dave_02_rodar_juiz.py configs/dave/mock.yaml && python scripts/dave_03_avaliar.py configs/dave/mock.yaml
pytest
```

## Resultados

### Lu: Pearson médio com as notas dos usuários (%)

| Avaliador | Pearson | IC 95% |
|---|---|---|
| Média do tipo da explicação (baseline ingênuo) | 28,8 | 24,8 a 33,2 |
| Qwen2.5-7B, sem contexto do usuário (E0) | 25,8 | 21,8 a 29,9 |
| Anotador humano 2 | 16,8 | 12,7 a 21,0 |
| Anotador humano 1 | 15,2 | 11,6 a 19,1 |
| Llama3.1-8B, E0 | 13,0 | 9,3 a 16,5 |

Dar o perfil do usuário à LLM piora o Qwen (demografia −5,0; preferências −7,6, ambas
significativas) e melhora o Llama (resumo do gosto +8,3). Detalhes em `resultados/local_qwen/` e
`resultados/local_llama/`.

### Dave: LLM no lugar dos 151 participantes

| Avaliador | Mesma conclusão do artigo (de 24) | Pearson médio com cada participante (%) |
|---|---|---|
| Acaso (notas sorteadas) | 10,8 (9 a 13) | — |
| Qwen2.5-7B | 15 | 8,5 |
| Llama3.1-8B | 15 | 9,9 |
| Média dos dois | 16 | 11,1 |
| Outro participante (referência humana) | — | 11,8 |

Nenhuma LLM inverte uma conclusão significativa do artigo. Ela acompanha os humanos em critérios
do texto ("informativo") e falha nos pessoais ("despertou meu interesse"). Detalhes em
`resultados/dave_local/resumo.md`.

## Organização

```
src/avaliador/
  comum/      LLMs (Ollama/OpenAI/mock), execução com cache, correlações e testes t (só numpy)
  lu/         dados, prompts e condições de contexto, baselines, meta-avaliação em 3 níveis
  dave/       dados, prompt do teste, comparação com os participantes
scripts/      dados_*, lu_01..03, dave_01..03
configs/      lu/ e dave/ (modelos, condições, paralelismo)
testes/       pytest (os testes que usam dados são pulados se os dados não estiverem baixados)
resultados/   saídas e respostas das LLMs, por experimento
```

As correlações e os testes t são implementados só com numpy porque o scipy é bloqueado em
alguns Windows; os testes conferem os valores com o scipy quando ele está disponível.

## Decisões de método

**Lu.** As condições de contexto (`so_demografia`, `so_resumo`, `so_preferencias`, e as
versões `foco_*`, que mandam julgar só a explicação) são comparadas com o E0 do mesmo modelo.
Nunca entram no prompt, para evitar vazamento: a explicação escrita pelo usuário, o motivo da nota,
as preferências marcadas no próprio filme avaliado e `pre_knowledge`. Em relação ao código de
Zhang et al., corrigimos o prompt de transparência (que usava a frase de persuasão; para
reproduzir o original, `reproduzir_bug_transparencia: true`) e dois erros do `corr.py`.

**Dave.** O prompt reproduz a tela do teste e as 8 frases do site original. As conclusões são
comparadas no nível do segue, com o mesmo teste do artigo (t pareado no geral, independente por
categoria). A referência humana de correlação é a média dos outros participantes que viram o
mesmo segue. O programa que gera os segues ainda não foi rodado: usamos os segues publicados.

## Referências

- Zhang, X. et al. Large Language Models as Evaluators for Recommendation Explanations.
  *RecSys 2024*. https://doi.org/10.1145/3640457.3688075
- Lu, H. et al. User Perception of Recommendation Explanation: Are Your Explanations What Users
  Need? *ACM Transactions on Information Systems*, 2023. https://doi.org/10.1145/3565480
- Gabbolini, G.; Bridge, D. Generating Interesting Song-to-Song Segues With Dave. *UMAP 2021*.
  https://doi.org/10.1145/3450613.3456819
