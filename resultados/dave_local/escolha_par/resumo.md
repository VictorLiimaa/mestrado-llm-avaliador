# Escolha no par: dave_local

Para cada participante e par, a preferência é a diferença de notas Dave − The Chain (o "jeito" da pessoa se cancela). Só pares em que a pessoa não empatou e vistos por 2+ participantes.

- `correlacao`: Pearson entre a diferença humana e a do previsor (empate do previsor = 0); IC 95% por bootstrap de participantes.
- `acordo`: quando o previsor escolhe um lado, quantas vezes é o mesmo da pessoa (acaso = 50%).
- `empate`: quantas vezes o previsor dá a mesma nota aos dois (não escolhe).
- `outro_humano`: média das diferenças dos outros participantes no mesmo par.
A preferência da LLM vem de duas notas pedidas separadamente.

## Média das 8 métricas (%)

| previsor                               |   correlacao_% |   ic_inf_% |   ic_sup_% |   acordo_% |   empate_% |
|:---------------------------------------|---------------:|-----------:|-----------:|-----------:|-----------:|
| outro_humano                           |           22.9 |       15.7 |       29.5 |       62   |       22.2 |
| qwen2.5-7b__E0                         |           12.3 |        6.9 |       17.7 |       63.9 |       65.3 |
| qwen2.5-7b__historico                  |            2.5 |       -4.2 |        9.4 |       54.2 |       65.3 |
| qwen2.5-7b__completo                   |            3.5 |       -3.5 |       10.2 |       53.4 |       65.4 |
| qwen2.5-7b__familiaridade              |            5.1 |       -0.9 |       10.7 |       55.9 |       72.2 |
| qwen2.5-7b__perfil                     |            6.9 |        1.3 |       13.2 |       59.5 |       75.4 |
| qwen2.5-7b__perfil_familiaridade       |            6.1 |        1.5 |       10.9 |       62   |       75.6 |
| llama3.1-8b__E0                        |           13.9 |        7.2 |       20.4 |       58.3 |       41.4 |
| llama3.1-8b__historico                 |           15.2 |        7.9 |       21.5 |       61.8 |       55.7 |
| llama3.1-8b__completo                  |           14.4 |        7.5 |       21   |       59.5 |       55.8 |
| llama3.1-8b__familiaridade             |            9.3 |        2.8 |       15.9 |       61.6 |       49.6 |
| llama3.1-8b__perfil                    |           11.1 |        5.5 |       16.8 |       58.8 |       57.7 |
| llama3.1-8b__perfil_familiaridade      |           12.1 |        6.6 |       17.3 |       61.8 |       61.8 |
| media-qwen-llama__E0                   |           15.7 |        8.9 |       22.3 |       59.9 |       35   |
| media-qwen-llama__historico            |           12.7 |        5.7 |       19.4 |       59.2 |       40.5 |
| media-qwen-llama__completo             |           12.5 |        5   |       19.2 |       58   |       42.6 |
| media-qwen-llama__familiaridade        |            9.6 |        3.2 |       16.3 |       58.4 |       41.9 |
| media-qwen-llama__perfil               |           11.6 |        5.7 |       17.3 |       58.8 |       48.2 |
| media-qwen-llama__perfil_familiaridade |           11   |        5.3 |       16.2 |       59.2 |       50.7 |

## Correlação por métrica (%)

| metrica          |   llama3.1-8b__E0 |   llama3.1-8b__completo |   llama3.1-8b__familiaridade |   llama3.1-8b__historico |   llama3.1-8b__perfil |   llama3.1-8b__perfil_familiaridade |   media-qwen-llama__E0 |   media-qwen-llama__completo |   media-qwen-llama__familiaridade |   media-qwen-llama__historico |   media-qwen-llama__perfil |   media-qwen-llama__perfil_familiaridade |   outro_humano |   qwen2.5-7b__E0 |   qwen2.5-7b__completo |   qwen2.5-7b__familiaridade |   qwen2.5-7b__historico |   qwen2.5-7b__perfil |   qwen2.5-7b__perfil_familiaridade |
|:-----------------|------------------:|------------------------:|-----------------------------:|-------------------------:|----------------------:|------------------------------------:|-----------------------:|-----------------------------:|----------------------------------:|------------------------------:|---------------------------:|-----------------------------------------:|---------------:|-----------------:|-----------------------:|----------------------------:|------------------------:|---------------------:|-----------------------------------:|
| creative         |               4.1 |                     7   |                          3.1 |                      6.6 |                  -1.6 |                                -3.9 |                    6.6 |                          6.3 |                               3.4 |                          11.1 |                        0.3 |                                      1.7 |           24.2 |             11.3 |                    2.3 |                         2.2 |                    11.2 |                  6.8 |                               13.7 |
| funny            |               3.6 |                    15.3 |                         -1.9 |                     13.2 |                   1.1 |                                11.8 |                    9.6 |                          8.5 |                              -3.8 |                           5   |                        9.9 |                                      1.5 |           30.9 |             11.1 |                   -5.8 |                        -4.4 |                    -7   |                 17.1 |                               -6.7 |
| high_quality     |              10.1 |                     8   |                          9.9 |                     12.9 |                  17.1 |                                11.1 |                   12   |                          8.8 |                               9.8 |                          11.2 |                       16.8 |                                     12.6 |           25.4 |             11.3 |                    4.8 |                         2.8 |                     1.8 |                  5.5 |                                8.5 |
| informative      |              47.2 |                    27.6 |                          8.8 |                     27.5 |                   7.1 |                                 6.8 |                   43.5 |                         22.6 |                               5.9 |                          25.9 |                       10.4 |                                      2.8 |           32.8 |             20.9 |                    6   |                        -6.6 |                     9.4 |                  9.3 |                               -3.7 |
| likeable         |              15.1 |                    14.3 |                         13.1 |                     20   |                  16.9 |                                16.9 |                   17.8 |                         16.1 |                              17.3 |                          16.5 |                       17.9 |                                     18.3 |           21.9 |             14.6 |                    9.7 |                        15.7 |                    -0.3 |                 12.7 |                               12.9 |
| sparked_interest |              -2.7 |                    15.8 |                         15   |                     22.6 |                  14.9 |                                21.6 |                   -2.7 |                         17.7 |                              16.6 |                          19   |                       13.7 |                                     17.2 |           12.2 |              0.6 |                   11   |                        10   |                     5.5 |                  6.3 |                                3.8 |
| understandable   |              13.1 |                    13.4 |                         23.3 |                     14.4 |                  23.7 |                                26.8 |                   17.9 |                         12.3 |                              24.6 |                          18.5 |                       17   |                                     28.9 |           29.7 |             21.5 |                    4.5 |                        19.5 |                    14.1 |                  1.6 |                               20.8 |
| well_written     |              20.7 |                    13.7 |                          2.8 |                      4.7 |                   9.3 |                                 5.8 |                   21   |                          7.7 |                               3   |                          -5.2 |                        6.5 |                                      4.7 |            5.9 |              7.5 |                   -4.5 |                         1.7 |                   -14.7 |                 -4   |                               -0.1 |
