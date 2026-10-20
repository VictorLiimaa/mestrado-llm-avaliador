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
python scripts/dave_04_treino_teste.py configs/dave/local.yaml # treino e teste por participante; ~900 chamadas por modelo
python scripts/dave_05_interestingness.py configs/dave/local.yaml  # nota do próprio Dave: reprodução e pesos aprendidos (sem LLM)
python scripts/dave_06_escolha_par.py configs/dave/local.yaml     # preferência no par derivada das notas (sem LLM)
python scripts/dave_07_par_direto.py configs/dave/local.yaml      # comparação direta no par, nas duas ordens
```

O passo 4 é o teste offline de treino e teste: para cada participante, um par vira teste, e o
prompt recebe informação sobre ele (enriquecimento): as notas que deu nos outros pares
(`historico`), as respostas sobre si no início do teste, com engajamento musical do Gold-MSI,
shows, tempo de escuta e inglês (`perfil`), se conhecia as músicas e os artistas do segue
(`familiaridade`), ou tudo junto (`completo`). As condições vêm de `treino_teste.condicoes` na
configuração. Compara com a média do
próprio participante, a média dos outros participantes e o E0. Com `--so-avaliar`, só recalcula
a comparação a partir do cache, sem chamar a LLM.

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

Um previsor sem LLM, a média que o próprio participante deu nos outros pares, chega a 28,3%
[21,2; 33,8]: boa parte da nota é o "jeito" de cada pessoa. Tirando esse jeito (correlação
dentro do participante), a média dos dois modelos fica em 12,8%, contra 15,7% de outro
participante. Detalhes em `resultados/dave_local/treino_teste/resumo.md`.

A fórmula do próprio Dave (interestingness) é um terceiro juiz automático. A reprodução bate
com o artigo: nos segues informativos, Spearman 0,25 / 0,23 / 0,22 (p < 0,001) com "likeable",
"high quality" e "understandable". Aprendendo os pesos da fórmula com treino e teste por segue,
ela chega a 14,6% nos segues do Dave, empatada com outro participante (14,4%) e acima da LLM
sem perfil (7,1% e 9,8%); com os pesos do artigo, fica em −0,6% (a fórmula só funciona nos segues
informativos). Detalhes em `resultados/dave_artigo/correlacoes_interestingness.md` e
`resultados/dave_local/pesos_aprendidos/resumo.md`.

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

## Correlação de Pearson e intervalos de confiança

Cada Pearson é reportado como o `scipy.stats.pearsonr`: coeficiente, p-valor bicaudal e intervalo
de confiança de 95% pela transformação de Fisher (`avaliador.comum.correlacao.pearson_ic`). Ao
lado, um segundo intervalo por bootstrap, reamostrando usuários. O de Fisher supõe que as notas
são independentes; quando a mesma pessoa avalia muitos itens, isso não vale e ele sai estreito
demais. No Lu (~65 explicações por usuário), o intervalo por bootstrap é cerca de 1,5 vez mais
largo que o de Fisher; no Dave (~6 avaliações por pessoa), praticamente igual. Arquivos:
`resultados/<experimento>/pearson_ic.csv` (Lu) e `*__correlacoes.csv` (Dave).

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
