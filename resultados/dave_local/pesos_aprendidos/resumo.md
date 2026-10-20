# Pesos da interestingness aprendidos com treino e teste

Treino e teste por segue (validação cruzada em 5 partes, repetida 10 vezes): um segue de teste nunca foi visto no treino. Spearman (%) com a nota de cada participante, nos segues do Dave; IC 95% por bootstrap de participantes; `dif` = diferença para os pesos do artigo (0,4 / 0,2 / 0,4). Previsor constante conta como 0.

## Todos os segues do Dave

### Média das 8 métricas (%)

| previsor         |   spearman_% |   ic_inf_% |   ic_sup_% |   dif_vs_pesos_artigo_% |   dif_ic_inf_% |   dif_ic_sup_% |
|:-----------------|-------------:|-----------:|-----------:|------------------------:|---------------:|---------------:|
| pesos_artigo     |         -0.6 |       -8   |        7   |                     0   |            0   |            0   |
| pesos_aprendidos |         14.6 |        9.1 |       19.9 |                    15.2 |            6.4 |           23.5 |
| outro_humano     |         14.4 |       10   |       19.2 |                    15   |            6.3 |           23.9 |
| qwen2.5-7b__E0   |          7.1 |        3.1 |       11.4 |                     7.8 |           -1.5 |           17.1 |
| llama3.1-8b__E0  |          9.8 |        4.1 |       15.2 |                    10.4 |           -0.4 |           21.1 |

### Por métrica (Spearman %)

| metrica          |   llama3.1-8b__E0 |   outro_humano |   pesos_aprendidos |   pesos_artigo |   qwen2.5-7b__E0 |
|:-----------------|------------------:|---------------:|-------------------:|---------------:|-----------------:|
| creative         |               1.2 |           14.4 |               22.6 |           -0.1 |              6.4 |
| funny            |              -0.6 |            9.4 |                1.3 |            1.3 |              5.2 |
| high_quality     |               8.2 |           17.4 |               14.8 |            2.5 |              1.9 |
| informative      |              45.3 |           25.6 |               31.6 |          -23.5 |             21.1 |
| likeable         |               5   |           19.6 |               12.9 |           10.8 |              8.6 |
| sparked_interest |               0.1 |            6   |               13.5 |           -1   |              0   |
| understandable   |               8.1 |           16.4 |                1.5 |            8.2 |             12.2 |
| well_written     |              11   |            6.2 |               18.4 |           -3.1 |              1.8 |

### Pesos aprendidos (média entre partes e repetições)

| metrica          |   raridade |   impopularidade |   concisao |
|:-----------------|-----------:|-----------------:|-----------:|
| creative         |       0.62 |             0.28 |       0.1  |
| funny            |       0.04 |             0.62 |       0.34 |
| high_quality     |       0.63 |             0.28 |       0.09 |
| informative      |       0.69 |             0.31 |       0    |
| likeable         |       0.59 |             0.21 |       0.2  |
| sparked_interest |       0.58 |             0.38 |       0.03 |
| understandable   |       0.41 |             0.34 |       0.25 |
| well_written     |       0.62 |             0.36 |       0.02 |

## Só os segues informativos

### Média das 8 métricas (%)

| previsor         |   spearman_% |   ic_inf_% |   ic_sup_% |   dif_vs_pesos_artigo_% |   dif_ic_inf_% |   dif_ic_sup_% |
|:-----------------|-------------:|-----------:|-----------:|------------------------:|---------------:|---------------:|
| pesos_artigo     |         17.4 |        8.5 |       25.2 |                     0   |            0   |            0   |
| pesos_aprendidos |         17.2 |        9.4 |       24.6 |                    -0.2 |           -3.5 |            3.2 |
| outro_humano     |          3.4 |       -2.8 |        9.2 |                   -14.1 |          -21.9 |           -5.2 |
| qwen2.5-7b__E0   |          5.8 |        0.2 |       11.5 |                   -11.6 |          -22.4 |           -0.3 |
| llama3.1-8b__E0  |          3.3 |       -3.3 |       10.3 |                   -14.1 |          -23.5 |           -4.2 |

### Por métrica (Spearman %)

| metrica          |   llama3.1-8b__E0 |   outro_humano |   pesos_aprendidos |   pesos_artigo |   qwen2.5-7b__E0 |
|:-----------------|------------------:|---------------:|-------------------:|---------------:|-----------------:|
| creative         |               1.2 |            2.9 |               17.5 |           18   |              1.3 |
| funny            |               5.7 |           -3.3 |                6.6 |           -1.5 |             13.7 |
| high_quality     |               6.8 |           10.5 |               19.6 |           24   |              9.3 |
| informative      |               1.2 |          -12.8 |               14.5 |           13.6 |             -8   |
| likeable         |               9.3 |           18.5 |               26.2 |           28.1 |             17   |
| sparked_interest |              -5.1 |            5.6 |               17   |           19.3 |              0   |
| understandable   |               2.5 |           14.9 |               22.5 |           22.8 |             14   |
| well_written     |               5.1 |           -9.3 |               13.4 |           15.3 |             -0.6 |

### Pesos aprendidos (média entre partes e repetições)

| metrica          |   raridade |   impopularidade |   concisao |
|:-----------------|-----------:|-----------------:|-----------:|
| creative         |       0.64 |             0.34 |       0.02 |
| funny            |       0.03 |             0.89 |       0.08 |
| high_quality     |       0.49 |             0.19 |       0.32 |
| informative      |       0.67 |             0.31 |       0.02 |
| likeable         |       0.36 |             0.15 |       0.49 |
| sparked_interest |       0.22 |             0.18 |       0.6  |
| understandable   |       0.3  |             0.24 |       0.45 |
| well_written     |       0.63 |             0.36 |       0.01 |
