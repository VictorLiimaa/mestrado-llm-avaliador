# Baseline do baseline: reprodução das linhas não-LLM da Tabela 1 (Zhang et al., 2024)

Pearson (%) entre o avaliador e as notas reais. Diferença = reproduzido - publicado.

| avaliador   |   dif_media_abs |   dif_max_abs |
|:------------|----------------:|--------------:|
| BLEU-1      |            1.38 |          4.47 |
| BLEU-4      |            6.38 |          9.95 |
| ROUGE-1-F   |            0.79 |          2.45 |
| ROUGE-L-F   |            1.03 |          2.2  |
| Annotator-1 |            0    |          0    |
| Annotator-2 |            0    |          0    |

| avaliador   | aspecto        | nivel   |   reproduzido |   publicado |   diferenca |
|:------------|:---------------|:--------|--------------:|------------:|------------:|
| BLEU-1      | persuasiveness | dataset |         12.23 |       11.68 |        0.55 |
| BLEU-1      | persuasiveness | user    |         16.03 |       15.84 |        0.19 |
| BLEU-1      | persuasiveness | pair    |         18.61 |       17.07 |        1.54 |
| BLEU-1      | transparency   | dataset |         11.6  |       10.06 |        1.54 |
| BLEU-1      | transparency   | user    |         15.34 |       12.69 |        2.65 |
| BLEU-1      | transparency   | pair    |         18.91 |       14.44 |        4.47 |
| BLEU-1      | accuracy       | dataset |          5.88 |        6.43 |       -0.55 |
| BLEU-1      | accuracy       | user    |         10.3  |       10.71 |       -0.41 |
| BLEU-1      | accuracy       | pair    |         13.27 |       12.18 |        1.09 |
| BLEU-1      | satisfaction   | dataset |         11.27 |       11.36 |       -0.09 |
| BLEU-1      | satisfaction   | user    |         14.19 |       12.91 |        1.28 |
| BLEU-1      | satisfaction   | pair    |         17.99 |       15.79 |        2.2  |
| BLEU-4      | persuasiveness | dataset |          8.78 |       -1.17 |        9.95 |
| BLEU-4      | persuasiveness | user    |         14.17 |        7.68 |        6.49 |
| BLEU-4      | persuasiveness | pair    |         16.06 |       13.53 |        2.53 |
| BLEU-4      | transparency   | dataset |          5.92 |       -3.47 |        9.39 |
| BLEU-4      | transparency   | user    |         10.43 |        4.13 |        6.3  |
| BLEU-4      | transparency   | pair    |         15.2  |       10.24 |        4.96 |
| BLEU-4      | accuracy       | dataset |          4.86 |       -4.63 |        9.49 |
| BLEU-4      | accuracy       | user    |          9.71 |        4.8  |        4.91 |
| BLEU-4      | accuracy       | pair    |         11.61 |        8.96 |        2.65 |
| BLEU-4      | satisfaction   | dataset |          9.26 |        0.61 |        8.65 |
| BLEU-4      | satisfaction   | user    |         13.76 |        6.86 |        6.9  |
| BLEU-4      | satisfaction   | pair    |         16.38 |       12.09 |        4.29 |
| ROUGE-1-F   | persuasiveness | dataset |         13.94 |       14.16 |       -0.22 |
| ROUGE-1-F   | persuasiveness | user    |         16.08 |       16.39 |       -0.31 |
| ROUGE-1-F   | persuasiveness | pair    |         15.92 |       17.56 |       -1.64 |
| ROUGE-1-F   | transparency   | dataset |         12.01 |       11.93 |        0.08 |
| ROUGE-1-F   | transparency   | user    |         12.94 |       12.74 |        0.2  |
| ROUGE-1-F   | transparency   | pair    |         12.75 |       14.45 |       -1.7  |
| ROUGE-1-F   | accuracy       | dataset |          9.03 |        8.61 |        0.42 |
| ROUGE-1-F   | accuracy       | user    |         10.6  |       11.02 |       -0.42 |
| ROUGE-1-F   | accuracy       | pair    |         10.38 |       12.83 |       -2.45 |
| ROUGE-1-F   | satisfaction   | dataset |         13.31 |       12.87 |        0.44 |
| ROUGE-1-F   | satisfaction   | user    |         13.02 |       13.2  |       -0.18 |
| ROUGE-1-F   | satisfaction   | pair    |         14.85 |       16.23 |       -1.38 |
| ROUGE-L-F   | persuasiveness | dataset |         13.98 |       14.16 |       -0.18 |
| ROUGE-L-F   | persuasiveness | user    |         15.64 |       16.39 |       -0.75 |
| ROUGE-L-F   | persuasiveness | pair    |         15.73 |       17.56 |       -1.83 |
| ROUGE-L-F   | transparency   | dataset |         11.36 |       11.93 |       -0.57 |
| ROUGE-L-F   | transparency   | user    |         12.32 |       12.74 |       -0.42 |
| ROUGE-L-F   | transparency   | pair    |         12.38 |       14.45 |       -2.07 |
| ROUGE-L-F   | accuracy       | dataset |          8.89 |        8.61 |        0.28 |
| ROUGE-L-F   | accuracy       | user    |         10.23 |       11.02 |       -0.79 |
| ROUGE-L-F   | accuracy       | pair    |         10.63 |       12.83 |       -2.2  |
| ROUGE-L-F   | satisfaction   | dataset |         12.74 |       12.87 |       -0.13 |
| ROUGE-L-F   | satisfaction   | user    |         12.12 |       13.2  |       -1.08 |
| ROUGE-L-F   | satisfaction   | pair    |         14.13 |       16.23 |       -2.1  |
| Annotator-1 | persuasiveness | dataset |         19.88 |       19.88 |        0    |
| Annotator-1 | persuasiveness | user    |         18.31 |       18.31 |       -0    |
| Annotator-1 | persuasiveness | pair    |         16.72 |       16.72 |       -0    |
| Annotator-1 | transparency   | dataset |         15.66 |       15.66 |        0    |
| Annotator-1 | transparency   | user    |         16.18 |       16.18 |        0    |
| Annotator-1 | transparency   | pair    |         11.31 |       11.31 |       -0    |
| Annotator-1 | accuracy       | dataset |         10.16 |       10.16 |        0    |
| Annotator-1 | accuracy       | user    |          9.78 |        9.78 |       -0    |
| Annotator-1 | accuracy       | pair    |          9.77 |        9.77 |        0    |
| Annotator-1 | satisfaction   | dataset |         14.93 |       14.93 |        0    |
| Annotator-1 | satisfaction   | user    |         13.28 |       13.28 |        0    |
| Annotator-1 | satisfaction   | pair    |         12.69 |       12.69 |       -0    |
| Annotator-2 | persuasiveness | dataset |         21.4  |       21.4  |        0    |
| Annotator-2 | persuasiveness | user    |         21.17 |       21.17 |        0    |
| Annotator-2 | persuasiveness | pair    |         20.9  |       20.9  |       -0    |
| Annotator-2 | transparency   | dataset |         25.97 |       25.97 |        0    |
| Annotator-2 | transparency   | user    |         26.42 |       26.42 |        0    |
| Annotator-2 | transparency   | pair    |         27.84 |       27.84 |        0    |
| Annotator-2 | accuracy       | dataset |         10.96 |       10.96 |       -0    |
| Annotator-2 | accuracy       | user    |         10.96 |       10.96 |       -0    |
| Annotator-2 | accuracy       | pair    |          9.32 |        9.32 |       -0    |
| Annotator-2 | satisfaction   | dataset |          8.86 |        8.86 |       -0    |
| Annotator-2 | satisfaction   | user    |          9.72 |        9.72 |       -0    |
| Annotator-2 | satisfaction   | pair    |          9.43 |        9.43 |       -0    |
