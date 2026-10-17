# Ouvinte simulado no teste do Dave: dave_local

150 participantes, 901 avaliações, 344 segues.


**Referência de acaso** (notas sorteadas, 20 sorteios): mesma conclusão em 10.8 de 24 em média (mín. 9, máx. 13); acordo no par 50.2%.


## qwen2.5-7b — E0

Respostas que não puderam ser lidas: 0.3%


### 1. Conclusões (Dave − The Chain, no nível do segue)

Mesma conclusão que os humanos em **15 de 24** comparações (mesma significância a 5% e, se significativa, mesmo sentido).


| grupo        | metrica          |   dif_humanos |   p_humanos |   dif_llm |   p_llm | mesmo_sinal   | mesma_conclusao   |
|:-------------|:-----------------|--------------:|------------:|----------:|--------:|:--------------|:------------------|
| geral        | likeable         |        -0.168 |       0.03  |    -0.187 |   0.001 | True          | True              |
| geral        | high_quality     |        -0.103 |       0.181 |    -0.088 |   0.043 | True          | False             |
| geral        | understandable   |        -0.09  |       0.242 |    -0.099 |   0.04  | True          | False             |
| geral        | sparked_interest |        -0.088 |       0.266 |    -0.012 |   0.319 | True          | True              |
| geral        | funny            |        -0.303 |       0     |    -0.269 |   0.002 | True          | True              |
| geral        | informative      |         0.252 |       0.002 |     0.327 |   0     | True          | True              |
| geral        | creative         |        -0.284 |       0     |    -0.058 |   0.025 | True          | True              |
| geral        | well_written     |         0.021 |       0.777 |    -0.088 |   0.163 | False         | True              |
| informativos | likeable         |         0.077 |       0.585 |    -0.212 |   0.02  | False         | False             |
| informativos | high_quality     |         0.084 |       0.559 |    -0.033 |   0.614 | False         | True              |
| informativos | understandable   |         0.16  |       0.241 |    -0.001 |   0.992 | False         | True              |
| informativos | sparked_interest |        -0.002 |       0.989 |     0.012 |   0.584 | False         | True              |
| informativos | funny            |        -0.259 |       0.016 |    -0.319 |   0.06  | True          | False             |
| informativos | informative      |         0.316 |       0.011 |     0.259 |   0.043 | True          | True              |
| informativos | creative         |        -0.301 |       0.014 |    -0.051 |   0.228 | True          | False             |
| informativos | well_written     |         0.182 |       0.157 |     0.133 |   0.079 | True          | True              |
| engracados   | likeable         |        -0.413 |       0     |    -0.214 |   0.003 | True          | True              |
| engracados   | high_quality     |        -0.371 |       0.001 |    -0.186 |   0.003 | True          | True              |
| engracados   | understandable   |        -0.345 |       0.01  |    -0.28  |   0     | True          | True              |
| engracados   | sparked_interest |        -0.294 |       0.015 |    -0.016 |   0.272 | True          | False             |
| engracados   | funny            |        -0.202 |       0.071 |    -0.36  |   0.001 | True          | False             |
| engracados   | informative      |        -0.208 |       0.045 |     0     |   0.996 | False         | False             |
| engracados   | creative         |        -0.295 |       0.009 |    -0.079 |   0.033 | True          | True              |
| engracados   | well_written     |        -0.193 |       0.083 |    -0.259 |   0.009 | True          | False             |


### 2. Correlação com cada participante (Pearson %, IC 95% por bootstrap)

`outro_humano` = média dos outros participantes que viram o mesmo segue (o quanto as pessoas concordam entre si).


| metrica          | avaliador    |   pearson_% |   spearman_% |   ic95_inf |   ic95_sup |   n |
|:-----------------|:-------------|------------:|-------------:|-----------:|-----------:|----:|
| likeable         | llm          |        9    |         9.08 |       2.09 |      15.52 | 802 |
| likeable         | outro_humano |       14.67 |        16.17 |       8.84 |      20.43 | 802 |
| high_quality     | llm          |        5.57 |         5.42 |      -1.11 |      12.65 | 800 |
| high_quality     | outro_humano |       13.22 |        13.67 |       6.39 |      20.44 | 800 |
| understandable   | llm          |       13.08 |        11.15 |       5.97 |      20.8  | 798 |
| understandable   | outro_humano |       18.45 |        17.33 |      11.24 |      25.11 | 798 |
| sparked_interest | llm          |        1.25 |         1.29 |      -6.06 |       8.79 | 801 |
| sparked_interest | outro_humano |        4.83 |         5.05 |      -2.48 |      12.21 | 801 |
| funny            | llm          |        9.47 |         8    |       1.69 |      16.56 | 801 |
| funny            | outro_humano |        6.72 |         7.05 |      -0.54 |      14.32 | 801 |
| informative      | llm          |       19.11 |        18.89 |      11.9  |      26.45 | 802 |
| informative      | outro_humano |       19.6  |        21.56 |      12.7  |      26.37 | 802 |
| creative         | llm          |        7.3  |         6.98 |       0.74 |      14.45 | 799 |
| creative         | outro_humano |       15.54 |        16.24 |       8.26 |      22.99 | 798 |
| well_written     | llm          |        3.5  |         3.44 |      -3.25 |      10.19 | 796 |
| well_written     | outro_humano |        1.48 |         5.14 |      -5.7  |       9.09 | 795 |


Média nas 8 métricas: LLM 8.53% | outro humano 11.81%


### 3. Escolha no par (acordo com o participante; acaso = 50%)


| metrica          |   acordo_% |   pares_sem_empate |   empate_humano_% |   empate_llm_% |
|:-----------------|-----------:|-------------------:|------------------:|---------------:|
| likeable         |      62.09 |                153 |             35.27 |          49.78 |
| high_quality     |      59.6  |                 99 |             32.96 |          65.7  |
| understandable   |      65.26 |                 95 |             44.94 |          62.7  |
| sparked_interest |      42.86 |                  7 |             38.03 |          97.99 |
| funny            |      72.22 |                 54 |             41.83 |          79.87 |
| informative      |      63.83 |                188 |             37.5  |          36.16 |
| creative         |      67.74 |                 31 |             40.58 |          88.79 |
| well_written     |      54.9  |                153 |             39.28 |          43.79 |



## llama3.1-8b — E0

Respostas que não puderam ser lidas: 0.0%


### 1. Conclusões (Dave − The Chain, no nível do segue)

Mesma conclusão que os humanos em **15 de 24** comparações (mesma significância a 5% e, se significativa, mesmo sentido).


| grupo        | metrica          |   dif_humanos |   p_humanos |   dif_llm |   p_llm | mesmo_sinal   | mesma_conclusao   |
|:-------------|:-----------------|--------------:|------------:|----------:|--------:|:--------------|:------------------|
| geral        | likeable         |        -0.168 |       0.03  |    -0.064 |   0.596 | True          | False             |
| geral        | high_quality     |        -0.103 |       0.181 |    -0.122 |   0.191 | True          | True              |
| geral        | understandable   |        -0.09  |       0.242 |    -0.18  |   0.092 | True          | True              |
| geral        | sparked_interest |        -0.088 |       0.266 |    -0.349 |   0     | True          | False             |
| geral        | funny            |        -0.303 |       0     |    -0.14  |   0.058 | True          | False             |
| geral        | informative      |         0.252 |       0.002 |     0.826 |   0     | True          | True              |
| geral        | creative         |        -0.284 |       0     |    -0.471 |   0     | True          | True              |
| geral        | well_written     |         0.021 |       0.777 |     0.285 |   0.001 | True          | False             |
| informativos | likeable         |         0.077 |       0.585 |    -0.232 |   0.254 | False         | True              |
| informativos | high_quality     |         0.084 |       0.559 |    -0.086 |   0.615 | False         | True              |
| informativos | understandable   |         0.16  |       0.241 |     0.198 |   0.198 | True          | True              |
| informativos | sparked_interest |        -0.002 |       0.989 |    -0.189 |   0.254 | True          | True              |
| informativos | funny            |        -0.259 |       0.016 |     0.048 |   0.559 | False         | False             |
| informativos | informative      |         0.316 |       0.011 |     1.043 |   0     | True          | True              |
| informativos | creative         |        -0.301 |       0.014 |    -0.232 |   0.156 | True          | False             |
| informativos | well_written     |         0.182 |       0.157 |     0.295 |   0.033 | True          | False             |
| engracados   | likeable         |        -0.413 |       0     |    -0.214 |   0.224 | True          | False             |
| engracados   | high_quality     |        -0.371 |       0.001 |    -0.347 |   0.011 | True          | True              |
| engracados   | understandable   |        -0.345 |       0.01  |    -0.623 |   0     | True          | True              |
| engracados   | sparked_interest |        -0.294 |       0.015 |    -0.472 |   0     | True          | True              |
| engracados   | funny            |        -0.202 |       0.071 |    -0.183 |   0.188 | True          | True              |
| engracados   | informative      |        -0.208 |       0.045 |    -0.429 |   0.002 | True          | True              |
| engracados   | creative         |        -0.295 |       0.009 |    -0.614 |   0     | True          | True              |
| engracados   | well_written     |        -0.193 |       0.083 |    -0.227 |   0.012 | True          | False             |


### 2. Correlação com cada participante (Pearson %, IC 95% por bootstrap)

`outro_humano` = média dos outros participantes que viram o mesmo segue (o quanto as pessoas concordam entre si).


| metrica          | avaliador    |   pearson_% |   spearman_% |   ic95_inf |   ic95_sup |   n |
|:-----------------|:-------------|------------:|-------------:|-----------:|-----------:|----:|
| likeable         | llm          |        8.63 |         8.05 |       1.3  |      16.22 | 802 |
| likeable         | outro_humano |       14.67 |        16.17 |       8.84 |      20.43 | 802 |
| high_quality     | llm          |        7.64 |         7.6  |       0.05 |      15.08 | 800 |
| high_quality     | outro_humano |       13.22 |        13.67 |       6.39 |      20.44 | 800 |
| understandable   | llm          |        6.2  |         5.38 |      -1.64 |      13.76 | 798 |
| understandable   | outro_humano |       18.45 |        17.33 |      11.24 |      25.11 | 798 |
| sparked_interest | llm          |       -0.41 |         0.03 |      -7.61 |       6.6  | 801 |
| sparked_interest | outro_humano |        4.83 |         5.05 |      -2.48 |      12.21 | 801 |
| funny            | llm          |        1.94 |         2.63 |      -6.71 |      10.67 | 801 |
| funny            | outro_humano |        6.72 |         7.05 |      -0.54 |      14.32 | 801 |
| informative      | llm          |       35.41 |        34.62 |      27.88 |      42.84 | 802 |
| informative      | outro_humano |       19.6  |        21.56 |      12.7  |      26.37 | 802 |
| creative         | llm          |        8.26 |        10.17 |       0.72 |      15.34 | 799 |
| creative         | outro_humano |       15.54 |        16.24 |       8.26 |      22.99 | 798 |
| well_written     | llm          |       11.63 |        11.27 |       4.14 |      18.74 | 796 |
| well_written     | outro_humano |        1.48 |         5.14 |      -5.7  |       9.09 | 795 |


Média nas 8 métricas: LLM 9.91% | outro humano 11.81%


### 3. Escolha no par (acordo com o participante; acaso = 50%)


| metrica          |   acordo_% |   pares_sem_empate |   empate_humano_% |   empate_llm_% |
|:-----------------|-----------:|-------------------:|------------------:|---------------:|
| likeable         |      55.23 |                172 |             35.41 |          41.43 |
| high_quality     |      53.4  |                191 |             33.11 |          37.58 |
| understandable   |      57.25 |                138 |             44.84 |          46.64 |
| sparked_interest |      48.55 |                173 |             38.17 |          37.28 |
| funny            |      57.5  |                 40 |             41.96 |          87.72 |
| informative      |      77.07 |                205 |             37.64 |          26.5  |
| creative         |      53.25 |                169 |             40.72 |          36.47 |
| well_written     |      58.29 |                187 |             39.19 |          28.83 |



## media-qwen-llama — E0

Respostas que não puderam ser lidas: 0.3%


### 1. Conclusões (Dave − The Chain, no nível do segue)

Mesma conclusão que os humanos em **16 de 24** comparações (mesma significância a 5% e, se significativa, mesmo sentido).


| grupo        | metrica          |   dif_humanos |   p_humanos |   dif_llm |   p_llm | mesmo_sinal   | mesma_conclusao   |
|:-------------|:-----------------|--------------:|------------:|----------:|--------:|:--------------|:------------------|
| geral        | likeable         |        -0.168 |       0.03  |    -0.129 |   0.076 | True          | False             |
| geral        | high_quality     |        -0.103 |       0.181 |    -0.105 |   0.072 | True          | True              |
| geral        | understandable   |        -0.09  |       0.242 |    -0.149 |   0.026 | True          | False             |
| geral        | sparked_interest |        -0.088 |       0.266 |    -0.19  |   0     | True          | False             |
| geral        | funny            |        -0.303 |       0     |    -0.193 |   0.002 | True          | True              |
| geral        | informative      |         0.252 |       0.002 |     0.579 |   0     | True          | True              |
| geral        | creative         |        -0.284 |       0     |    -0.272 |   0     | True          | True              |
| geral        | well_written     |         0.021 |       0.777 |     0.096 |   0.079 | True          | True              |
| informativos | likeable         |         0.077 |       0.585 |    -0.222 |   0.07  | False         | True              |
| informativos | high_quality     |         0.084 |       0.559 |    -0.06  |   0.554 | False         | True              |
| informativos | understandable   |         0.16  |       0.241 |     0.099 |   0.263 | True          | True              |
| informativos | sparked_interest |        -0.002 |       0.989 |    -0.089 |   0.291 | True          | True              |
| informativos | funny            |        -0.259 |       0.016 |    -0.135 |   0.184 | True          | False             |
| informativos | informative      |         0.316 |       0.011 |     0.651 |   0     | True          | True              |
| informativos | creative         |        -0.301 |       0.014 |    -0.141 |   0.104 | True          | False             |
| informativos | well_written     |         0.182 |       0.157 |     0.214 |   0.006 | True          | False             |
| engracados   | likeable         |        -0.413 |       0     |    -0.22  |   0.039 | True          | True              |
| engracados   | high_quality     |        -0.371 |       0.001 |    -0.271 |   0.001 | True          | True              |
| engracados   | understandable   |        -0.345 |       0.01  |    -0.465 |   0     | True          | True              |
| engracados   | sparked_interest |        -0.294 |       0.015 |    -0.254 |   0     | True          | True              |
| engracados   | funny            |        -0.202 |       0.071 |    -0.257 |   0.009 | True          | False             |
| engracados   | informative      |        -0.208 |       0.045 |    -0.214 |   0.027 | True          | True              |
| engracados   | creative         |        -0.295 |       0.009 |    -0.357 |   0     | True          | True              |
| engracados   | well_written     |        -0.193 |       0.083 |    -0.246 |   0     | True          | False             |


### 2. Correlação com cada participante (Pearson %, IC 95% por bootstrap)

`outro_humano` = média dos outros participantes que viram o mesmo segue (o quanto as pessoas concordam entre si).


| metrica          | avaliador    |   pearson_% |   spearman_% |   ic95_inf |   ic95_sup |   n |
|:-----------------|:-------------|------------:|-------------:|-----------:|-----------:|----:|
| likeable         | llm          |       10.14 |         9.85 |       2.58 |      17.6  | 802 |
| likeable         | outro_humano |       14.67 |        16.17 |       8.84 |      20.43 | 802 |
| high_quality     | llm          |        8.11 |         8.29 |       0.76 |      15.23 | 800 |
| high_quality     | outro_humano |       13.22 |        13.67 |       6.39 |      20.44 | 800 |
| understandable   | llm          |        9.35 |         9.61 |       1.79 |      17.19 | 798 |
| understandable   | outro_humano |       18.45 |        17.33 |      11.24 |      25.11 | 798 |
| sparked_interest | llm          |       -0.27 |         0.01 |      -7.4  |       6.85 | 801 |
| sparked_interest | outro_humano |        4.83 |         5.05 |      -2.48 |      12.21 | 801 |
| funny            | llm          |        7.25 |         5.89 |      -1.22 |      15.2  | 801 |
| funny            | outro_humano |        6.72 |         7.05 |      -0.54 |      14.32 | 801 |
| informative      | llm          |       33.13 |        31.9  |      25.29 |      40.41 | 802 |
| informative      | outro_humano |       19.6  |        21.56 |      12.7  |      26.37 | 802 |
| creative         | llm          |        9.51 |        11.29 |       2.27 |      16.14 | 799 |
| creative         | outro_humano |       15.54 |        16.24 |       8.26 |      22.99 | 798 |
| well_written     | llm          |       11.29 |        11.92 |       3.72 |      18.76 | 796 |
| well_written     | outro_humano |        1.48 |         5.14 |      -5.7  |       9.09 | 795 |


Média nas 8 métricas: LLM 11.06% | outro humano 11.81%


### 3. Escolha no par (acordo com o participante; acaso = 50%)


| metrica          |   acordo_% |   pares_sem_empate |   empate_humano_% |   empate_llm_% |
|:-----------------|-----------:|-------------------:|------------------:|---------------:|
| likeable         |      57.14 |                203 |             35.27 |          30.58 |
| high_quality     |      52.58 |                213 |             32.96 |          28.7  |
| understandable   |      61.01 |                159 |             44.94 |          38.2  |
| sparked_interest |      48.33 |                180 |             38.03 |          35.35 |
| funny            |      64.29 |                 70 |             41.83 |          74.94 |
| informative      |      71.74 |                230 |             37.5  |          20.31 |
| creative         |      53.45 |                174 |             40.58 |          33.86 |
| well_written     |      60.5  |                200 |             39.28 |          25.28 |

