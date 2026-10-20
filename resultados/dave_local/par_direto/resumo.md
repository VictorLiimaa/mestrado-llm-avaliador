# Comparação direta no par: dave_local

A LLM vê os dois segues de um par e diz qual descreve melhor cada afirmação para a pessoa; cada par nas duas ordens (Dave como A e como B). Preferência prevista: +1 Dave, −1 The Chain, 0 quando as duas ordens se contradizem. Mesmas medidas da escolha no par (passo 6): `correlacao` (principal, IC 95% por bootstrap de participantes), `acordo` (acaso = 50%), `empate` (aqui: as duas ordens se contradisseram). `notas_E0` = preferência derivada das notas separadas do passo 2.

## Média das 8 métricas (%)

| previsor                       |   correlacao_% |   ic_inf_% |   ic_sup_% |   acordo_% |   empate_% |
|:-------------------------------|---------------:|-----------:|-----------:|-----------:|-----------:|
| outro_humano                   |           22.9 |       15.7 |       29.5 |       62.1 |       22.2 |
| qwen2.5-14b__par_E0            |           16.6 |       10.2 |       23.2 |       62.1 |       35.2 |
| qwen2.5-14b__par_perfil        |           16   |        8.6 |       23   |       61.8 |       44.4 |
| qwen2.5-14b__par_familiaridade |           16.2 |        9.4 |       23   |       62.3 |       38.8 |
| qwen2.5-14b__par_historico     |           14.9 |        7   |       22   |       59.8 |       33   |
| qwen2.5-14b__par_completo      |           14.8 |        7   |       22.4 |       60.5 |       38.2 |
| qwen2.5-14b__notas_E0          |           14.4 |        6.9 |       22   |       63.1 |       44   |

## Correlação por métrica (%)

| metrica          |   outro_humano |   qwen2.5-14b__notas_E0 |   qwen2.5-14b__par_E0 |   qwen2.5-14b__par_completo |   qwen2.5-14b__par_familiaridade |   qwen2.5-14b__par_historico |   qwen2.5-14b__par_perfil |
|:-----------------|---------------:|------------------------:|----------------------:|----------------------------:|---------------------------------:|-----------------------------:|--------------------------:|
| creative         |           24.2 |                     1.1 |                   3.6 |                        11.2 |                              2.7 |                         14.8 |                       7.9 |
| funny            |           30.9 |                    11.7 |                  10.8 |                        15.5 |                              8.4 |                         12.2 |                       7.7 |
| high_quality     |           25.5 |                     8.7 |                  12   |                        12   |                             16.5 |                         15.9 |                      17.2 |
| informative      |           33   |                    33.9 |                  35.4 |                        28   |                             36.3 |                         28.4 |                      27.2 |
| likeable         |           21.9 |                    16.1 |                  14.4 |                         9.5 |                             14.5 |                         11.1 |                      16.7 |
| sparked_interest |           12.2 |                    14.8 |                  21.3 |                        20.7 |                             20.2 |                         13.7 |                      19.9 |
| understandable   |           29.7 |                    24.2 |                  20   |                        11.7 |                             20.9 |                          9.9 |                      12.6 |
| well_written     |            5.9 |                     5   |                  15.3 |                        10.1 |                             10.5 |                         13.4 |                      18.5 |

## Viés de posição: mesma escolha nas duas ordens (%)

| previsor                       |   mesma_escolha_nas_duas_ordens_% |   falhas_% |
|:-------------------------------|----------------------------------:|-----------:|
| qwen2.5-14b__par_E0            |                              63.5 |        0   |
| qwen2.5-14b__par_completo      |                              60.6 |        0   |
| qwen2.5-14b__par_familiaridade |                              60.4 |        0   |
| qwen2.5-14b__par_historico     |                              65.1 |        0   |
| qwen2.5-14b__par_perfil        |                              55   |        0.3 |
