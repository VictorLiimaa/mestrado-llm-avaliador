# Dados

Os dados não são redistribuídos neste repositório. Os dois scripts abaixo os colocam nas pastas
certas e conferem, por MD5, que são exatamente os arquivos usados nos experimentos.

## `lu/`: explicações de filmes (Lu et al., 2023)

```bash
python scripts/dados_baixar_lu.py
```

Baixa do repositório de Zhang et al. (2024), https://github.com/Xiaoyu-SZ/LLMasEvaluator, os dados
coletados por Lu et al. (2023): 39 usuários, 2.536 explicações em chinês, 9 tipos de explicação.

| Arquivo | Conteúdo |
|---|---|
| `df_explanation.pkl` | Estudo completo: notas dos usuários e contexto (52 colunas) |
| `third_party.csv` | Notas de dois anotadores externos e o texto limpo das explicações |
| `df_explanation_selected.csv` | Id numérico dos usuários, que liga aos dados demográficos |
| `user_demo.csv` | Dados demográficos |

Os arquivos estão alinhados linha a linha; `avaliador.lu.dados.carregar` confere o alinhamento.

## `dave/`: teste com usuários do Dave (Gabbolini & Bridge, 2021)

1. Baixe o arquivo do Zenodo: https://doi.org/10.5281/zenodo.4618570
2. Rode, apontando para o `.zip` baixado ou para a pasta `res` descompactada:

```bash
python scripts/dados_preparar_dave.py caminho/para/arquivo.zip
```

| Arquivo | Conteúdo |
|---|---|
| `answers.json` | Respostas dos 158 participantes (151 após o filtro do artigo): notas de 6 segues em 8 critérios, engajamento musical (Gold-MSI), nível de inglês e familiaridade |
| `df_segue_category_dave.csv`, `df_segue_category_the_chain.csv` | Texto de cada segue e categoria (F = engraçado, I = informativo), atribuída pelos autores |
| `user_trial_sample/*.json` | Para cada par: música inicial, segunda música de cada sistema, os dois segues e o score de *interestingness* do Dave. O nome do arquivo é o identificador usado nas respostas |

O `comments.json` do Zenodo não é copiado: tem comentários livres dos participantes, e um deles
traz dados de contato.

## Referências

- Lu, H. et al. User Perception of Recommendation Explanation: Are Your Explanations What Users
  Need? *ACM Transactions on Information Systems*, 2023. https://doi.org/10.1145/3565480
- Zhang, X. et al. Large Language Models as Evaluators for Recommendation Explanations.
  *RecSys 2024*. https://doi.org/10.1145/3640457.3688075
- Gabbolini, G.; Bridge, D. Generating Interesting Song-to-Song Segues With Dave. *UMAP 2021*.
  https://doi.org/10.1145/3450613.3456819
