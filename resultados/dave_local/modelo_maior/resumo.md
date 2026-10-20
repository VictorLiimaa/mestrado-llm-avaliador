# Modelo maior: Qwen2.5-14B no E0 do Dave (19/10/2026)

Mesmo prompt e mesmas 344 avaliações do E0 do Qwen2.5-7B e do Llama3.1-8B. Rodado localmente
(Ollama; 10 GB, 57% CPU / 43% GPU numa RTX 3050 de 6 GB; ~2,5 s por resposta). Controle de
qualidade: 0 respostas ilegíveis, 94 respostas distintas (Qwen 7B: 44), nenhuma cópia do exemplo.
A comparação direta no par com o 14B não foi rodada.

## Simulação do teste com usuários (como no passo 3)

| Modelo | Mesma conclusão do artigo (de 24) | Pearson com cada participante (%) | Acordo no par (%) |
|---|---|---|---|
| Acaso | 10,8 (9 a 13) | — | 50 |
| Qwen2.5-7B | 15 | 8,5 | 61,1 |
| Llama3.1-8B | 15 | 9,9 | 57,6 |
| **Qwen2.5-14B** | **17** | **13,8** [10,1; 17,5] | 62,8 |
| Outro participante | — | 11,8 | — |

- 14B contra 7B (mesma família): +5,3 [2,0; 8,6], significativo.
- 14B contra a média dos dois modelos pequenos: +2,8 [−0,8; 6,5], não significativo.
- "sparked interest": 7B 1,2 [−6,4; 8,2] → 14B 10,9 [3,7; 17,6].
- Nenhuma conclusão significativa dos humanos sai invertida.

## Treino e teste por participante (passo 4, só E0)

| Previsor | Pearson | Dentro do participante |
|---|---|---|
| Média do próprio participante | 28,3 | não se aplica |
| Qwen2.5-14B | 13,8 | 14,9 [10,0; 19,4] |
| Outro participante | 11,8 | 15,7 |
| Média Qwen 7B + Llama 8B | 11,0 | 12,8 |

## Escolha no par derivada das notas (passo 6)

14B: 14,4 [6,9; 22,0], acordo 63%, empata 44%. Média dos pequenos: 15,7. Outro participante: 22,9.

## Pesos da interestingness (passo 5, nos segues do Dave)

Pesos aprendidos 14,6; outro participante 14,4; 14B 11,4 [6,5; 16,2]; média dos pequenos 10,5.

## Calibração (médias de 1 a 5)

| | likeable | high_quality | understandable | sparked_interest | funny | informative | creative | well_written |
|---|---|---|---|---|---|---|---|---|
| Humanos | 3,18 | 3,08 | 3,73 | 2,97 | 2,69 | 3,13 | 3,43 | 3,32 |
| Qwen2.5-14B | 3,45 | 3,55 | 2,97 | 3,43 | 1,32 | 2,83 | 3,96 | 3,57 |
| Qwen2.5-7B | 3,57 | 3,79 | 3,73 | 4,00 | 2,30 | 3,74 | 4,94 | 4,12 |

## Comparação direta no par com o 14B (versão 2 do prompt, E0, 344 perguntas)

Controle de qualidade: 1 resposta ilegível, 35 respostas distintas, nenhum "?" (os modelos de 7–8B
deixaram 8–10%).

| | Qwen 7B | Llama 8B | **Qwen 14B** |
|---|---|---|---|
| Escolhe "B" (segunda posição) | 67% | 52% | 61% |
| Mesma escolha nas duas ordens (acaso = 50%) | 32% | 41% | **63,5%** |
| Correlação com a preferência humana (direta) | 6,1 | 10,7 | **16,6** [10,2; 23,2] |
| Correlação a partir das notas separadas | 12,3 | 13,9 | 14,4 |
| Outro participante | 22,9 | 22,9 | 22,9 |

- 14B direto contra 7B direto: +10,5 [3,7; 18,2], significativo.
- 14B direto contra 14B com notas separadas: +2,1 [−3,4; 8,1], não significativo.
- Consistência entre as ordens, por critério: 70–76% em likeable, high_quality, understandable,
  sparked_interest e funny; 42–53% em informative, creative e well_written.
- Correlação por critério: informative 35,4 [23,0; 46,9]; sparked_interest 21,3 [8,5; 33,0];
  understandable 20,0; creative 3,6 (o mais fraco).
