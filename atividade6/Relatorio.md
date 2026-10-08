## Passo 5 — Tabela de resultados

Abaixo estão os resultados das execuções utilizando o solver HiGHS com tempo limite de 1800 segundos (30 minutos).

| Instância | Cidades ($n$) | Formulação | Solver | LB | UB | GAP | Tempo (s) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| berlin52 | 52 | MTZ | HiGHS | 7544.37 | 7544.37 | 0.000000 | 11.48 | Optimal |
| berlin52 | 52 | MCF | HiGHS | 7543.65 | 7544.37 | 0.000095 | 4.70 | Optimal |
| kroA100 | 100 | MTZ | HiGHS | 21283.32 | 21285.44 | 0.000100 | 520.44 | Optimal |
| kroA100 | 100 | MCF | HiGHS | 21283.42 | 21285.44 | 0.000095 | 256.85 | Optimal |
| ch150 | 150 | MTZ | HiGHS | 6431.35 | 6712.62 | 0.041902 | 1800.13 | Time limit reached |
| ch150 | 150 | MCF | HiGHS | 6459.30 | 6735.66 | 0.041029 | 1800.28 | Time limit reached |
| kroA200 | 200 | MTZ | HiGHS | 28313.66 | 33534.26 | 0.155680 | 1800.48 | Time limit reached |
| kroA200 | 200 | MCF | HiGHS | 28985.65 | 32312.53 | 0.102960 | 1800.79 | Time limit reached |

(Nota: A instância dj38 foi testada, mas não incluída nesta tabela por não fazer parte da lista requisitada no roteiro).

## Passo 6 — Análise

*Evolução do GAP da MTZ:*
O GAP da MTZ evoluiu drasticamente conforme o crescimento das instâncias. Para berlin52 (52 cidades) e kroA100 (100 cidades), o solver conseguiu fechar a otimalidade dentro do tempo com GAP virtualmente nulo. No entanto, para ch150, ao atingir o limite de 30 minutos, restou um GAP de cerca de 4,19%. Já na instância maior, kroA200, o GAP disparou para 15,56%. Esse comportamento é perfeitamente coerente com o que foi discutido em aula: o limitante inferior da MTZ é excessivamente fraco. Com o aumento exponencial das rotas possíveis devido ao crescimento de $n$, a relaxação linear fraca falha em realizar podas eficientes na árvore de busca, travando o progresso da solução.

*Desempenho e Impraticabilidade da MCF:*
Diferente do esperado para ambientes com memória mais limitada, o modelo MCF (Fluxo Multi-Produto) não se mostrou impraticável por restrição de memória (OOM - Out of Memory) durante os testes. Nas instâncias maiores (ch150 e kroA200), o modelo foi gerado com sucesso e submetido ao solver, que foi interrompido apenas pelo tempo limite de 1800 segundos. Porém, é notável o impacto do crescimento de $O(n^3)$ nas variáveis: apesar de processar, o solver gastou considerável esforço de máquina e não conseguiu fechar a otimalidade no tempo hábil nas duas instâncias maiores, ilustrando que, embora forte, o peso computacional a torna muito lenta em CH150.

*Comparação de Limite Inferior (LB - MTZ vs MCF):*
Nas instâncias em que o tempo acabou, ficou evidente a superioridade matemática da MCF. Na instância kroA200, o limite inferior (LB) estabelecido pela MCF foi 28985.65, enquanto a MTZ ficou bem atrás com um LB de 28313.66. Isso reflete diretamente no GAP final: a MCF terminou com GAP de 10,2% contra 15,5% da MTZ no exato mesmo limite de tempo. Isso confirma que a MCF é, de fato, uma formulação mais apertada, limitando muito melhor o espaço de busca do que a formulação clássica da MTZ.

*Solvers Utilizados:*
O grupo utilizou apenas o solver HiGHS em todas as execuções. Portanto, não houve comparação direta de desempenho ou de uso de memória com o solver Gurobi.

*Comparação de Ótimos (Valores da TSPLIB):*
Para as execuções em que a rota ótima foi encontrada, os valores não coincidem perfeitamente com os reportados pela tabela da TSPLIB. O ótimo conhecido para berlin52 é 7542, mas o modelo retornou 7544.37. Para kroA100, o ótimo é 21282, e encontramos 21285.44. Esta pequena diferença ocorre porque a matriz de distâncias $d_{ij}$ provavelmente não foi arredondada para o inteiro mais próximo em cada cálculo utilizando a convenção EUC_2D, resultando no acúmulo de frações ao longo da rota ótima.

*O Compromisso (Trade-off): MTZ vs MCF na Prática:*
Os resultados demonstraram com clareza o compromisso estrutural. A MTZ (compacta e fraca) é rápida para modelar e consegue resolver instâncias até 100 nós, mas é ineficiente em instâncias maiores devido à qualidade do Limitante Inferior. Por outro lado, a MCF (compacta e forte) possui um Limitante Inferior potente, superando a MTZ na mesma janela de tempo para grandes instâncias, mas cobra o preço de ser pesada computacionalmente com o aumento de $n$.
Em uma situação prática: Optaríamos pela MTZ apenas se houvesse rigorosa restrição de memória que inviabilizasse carregar a matriz da MCF. Optaríamos pela MCF quando a qualidade do limitante e um GAP mais apertado em tempos curtos fossem cruciais, assumindo disponibilidade de RAM.
