# Comparação direta no par, versão 1 (descartada como resultado principal)

O prompt desta versão terminava com "Example: A B B A A B A B". Controle de qualidade das respostas:

| Modelo | Respostas iguais ao exemplo | Mesma escolha nas duas ordens (acaso = 50%) |
|---|---|---|
| Qwen2.5-7B | 21% a 92%, conforme a condição | 2% a 25% |
| Llama3.1-8B | 0% a 1% | 25% a 29% |

O Qwen copiou o exemplo; o Llama não copiou, mas respondeu quase sempre os mesmos padrões de letras
(8 respostas distintas em 344 pares no E0), independentemente de qual segue estava em A: viés de
posição. Correlação com a preferência humana: perto de zero (Qwen + Llama, E0: 3,8%), abaixo da
preferência derivada das notas separadas (15,7%).

A versão 2 (respostas em cache/*__par2_*.jsonl) tira o exemplo do prompt. As respostas da versão 1
estão em cache/*__par_*.jsonl e ficam guardadas como registro.
