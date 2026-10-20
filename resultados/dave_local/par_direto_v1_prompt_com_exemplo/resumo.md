# Comparação direta no par: dave_local

A LLM vê os dois segues de um par e diz qual descreve melhor cada afirmação para a pessoa; cada par nas duas ordens (Dave como A e como B). Preferência prevista: +1 Dave, −1 The Chain, 0 quando as duas ordens se contradizem. Mesmas medidas da escolha no par (passo 6): `correlacao` (principal, IC 95% por bootstrap de participantes), `acordo` (acaso = 50%), `empate` (aqui: as duas ordens se contradisseram). `notas_E0` = preferência derivada das notas separadas do passo 2.

## Média das 8 métricas (%)

| previsor                            |   correlacao_% |   ic_inf_% |   ic_sup_% |   acordo_% |   empate_% |
|:------------------------------------|---------------:|-----------:|-----------:|-----------:|-----------:|
| outro_humano                        |           26.8 |       19.4 |       33.8 |       64.7 |       20.9 |
| qwen2.5-7b__par_E0                  |            5.2 |        1.7 |        8.7 |       61.1 |       90.4 |
| qwen2.5-7b__par_perfil              |           -0.1 |       -5.6 |        5.2 |       52.3 |       82.2 |
| qwen2.5-7b__par_familiaridade       |            2.6 |       -2   |        7.2 |       57.2 |       91.7 |
| qwen2.5-7b__par_completo            |            3.2 |       -2.5 |        8.8 |       52.2 |       45.8 |
| qwen2.5-7b__par_historico           |            4.1 |       -0.9 |        9.4 |       54   |       29.6 |
| qwen2.5-7b__notas_E0                |           10.9 |        3.7 |       17.5 |       63.6 |       64.9 |
| llama3.1-8b__par_E0                 |            3   |       -1.3 |        6.1 |       62.7 |       69.5 |
| llama3.1-8b__par_perfil             |            3.1 |       -1.7 |        7.5 |       51.9 |       71.8 |
| llama3.1-8b__par_familiaridade      |           -1.6 |       -5   |        1.9 |       48.9 |       71.8 |
| llama3.1-8b__par_completo           |            4.7 |       -0.9 |       10.6 |       53.1 |       65.6 |
| llama3.1-8b__par_historico          |            8.1 |        3.3 |       13.6 |       52.9 |       68.6 |
| llama3.1-8b__notas_E0               |           13.2 |        5.7 |       20.5 |       57.5 |       41.9 |
| media-qwen-llama__par_E0            |            3.8 |       -0.4 |        7.8 |       54.1 |       64.4 |
| media-qwen-llama__par_perfil        |            3.1 |       -2.6 |        8.6 |       54.1 |       60.6 |
| media-qwen-llama__par_familiaridade |           -0.4 |       -5.6 |        4.5 |       52.3 |       67.4 |
| media-qwen-llama__par_completo      |            6.1 |       -0.1 |       12.2 |       54.5 |       38.2 |
| media-qwen-llama__par_historico     |            8.7 |        3.6 |       14.3 |       55.7 |       29.9 |

## Correlação por métrica (%)

| metrica          |   llama3.1-8b__notas_E0 |   llama3.1-8b__par_E0 |   llama3.1-8b__par_completo |   llama3.1-8b__par_familiaridade |   llama3.1-8b__par_historico |   llama3.1-8b__par_perfil |   media-qwen-llama__par_E0 |   media-qwen-llama__par_completo |   media-qwen-llama__par_familiaridade |   media-qwen-llama__par_historico |   media-qwen-llama__par_perfil |   outro_humano |   qwen2.5-7b__notas_E0 |   qwen2.5-7b__par_E0 |   qwen2.5-7b__par_completo |   qwen2.5-7b__par_familiaridade |   qwen2.5-7b__par_historico |   qwen2.5-7b__par_perfil |
|:-----------------|------------------------:|----------------------:|----------------------------:|---------------------------------:|-----------------------------:|--------------------------:|---------------------------:|---------------------------------:|--------------------------------------:|----------------------------------:|-------------------------------:|---------------:|-----------------------:|---------------------:|---------------------------:|--------------------------------:|----------------------------:|-------------------------:|
| creative         |                     3   |                  -5   |                         2.6 |                            -20   |                         11   |                      -1.7 |                       -6.3 |                              3.1 |                                 -17.1 |                              15.3 |                           -4.6 |           30.7 |                    8.3 |                 -4.2 |                        2   |                            11   |                         9.8 |                     -6.8 |
| funny            |                     3.1 |                 -10.4 |                        12.5 |                             -6   |                         20.2 |                       4.7 |                       10.9 |                             21.4 |                                  -5.1 |                              32.5 |                            1.7 |           40.3 |                    5.1 |                 18.2 |                       18.3 |                            -1.3 |                        25.7 |                     -3.1 |
| high_quality     |                    10.3 |                   7.8 |                        19.2 |                             20   |                         13.6 |                      12.2 |                       12.9 |                              9.1 |                                  23.4 |                               1.6 |                            9.8 |           26.8 |                    8.8 |                 13.6 |                       -3.4 |                            12.1 |                       -10.9 |                     -0.3 |
| informative      |                    47   |                   0.2 |                        10.9 |                            -13.5 |                         15.1 |                      -2   |                        7.1 |                              8.8 |                                 -12   |                              12.2 |                           -1.2 |           30.4 |                   21.3 |                 20   |                        1.6 |                             3.5 |                         3.7 |                      1.2 |
| likeable         |                    14.6 |                   8.4 |                        -9.8 |                              0   |                         -3.3 |                       6   |                       -5.1 |                              4.9 |                                  -7.6 |                               6.5 |                            0.8 |           25.7 |                   13.1 |                 -7.9 |                        9.5 |                            -7.6 |                         7.5 |                     -3.2 |
| sparked_interest |                    -3.6 |                   9.6 |                         4.4 |                              6.2 |                          2.5 |                       4.3 |                        5.8 |                             17.7 |                                  14.6 |                              12   |                            4.4 |           14.2 |                    6.8 |                  0.6 |                       18.3 |                            14   |                        14   |                      1.2 |
| understandable   |                    15.3 |                  12.9 |                        -5.3 |                              0   |                         -0.1 |                       0   |                        5.4 |                            -14.1 |                                   4.3 |                              -8.7 |                           14.3 |           34.8 |                   19.9 |                  2.1 |                      -14   |                             4.3 |                        -9.7 |                     14.3 |
| well_written     |                    16.1 |                   0.4 |                         3.2 |                              0.5 |                          6.2 |                       1.3 |                        0.2 |                             -1.9 |                                  -4.1 |                              -1.6 |                           -0.7 |           11.8 |                    3.5 |                 -0.5 |                       -6.6 |                           -15.2 |                        -7.6 |                     -4.3 |

## Viés de posição: mesma escolha nas duas ordens (%)

| previsor                       |   mesma_escolha_nas_duas_ordens_% |   falhas_% |
|:-------------------------------|----------------------------------:|-----------:|
| llama3.1-8b__par_E0            |                              29.3 |        0   |
| llama3.1-8b__par_completo      |                              24.9 |        5.3 |
| llama3.1-8b__par_familiaridade |                              27.7 |        0   |
| llama3.1-8b__par_historico     |                              27.3 |        2   |
| llama3.1-8b__par_perfil        |                              27.6 |        0   |
| qwen2.5-7b__par_E0             |                               1.8 |        4.4 |
| qwen2.5-7b__par_completo       |                              24.7 |       28.3 |
| qwen2.5-7b__par_familiaridade  |                               4.9 |        1.9 |
| qwen2.5-7b__par_historico      |                              11.8 |       46.9 |
| qwen2.5-7b__par_perfil         |                               5   |        6.6 |
