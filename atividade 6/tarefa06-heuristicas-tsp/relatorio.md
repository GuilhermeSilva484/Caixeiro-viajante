# Relatório - Heurísticas para TSP (Vizinho Mais Próximo e Construção Aleatória)

## Passo 4 — Tabela de resultados

| Instância | Cidades (n) | Ótimo conhecido | NN cidade 1 - Custo | NN cidade 1 - GAP | NN cidade 1 - Tempo (s) | NN multi-start - Custo | NN multi-start - GAP | NN multi-start - Tempo (s) | Aleatória - Custo médio | Aleatória - Desvio padrão | Aleatória - Melhor custo | Aleatória - GAP (melhor) | Aleatória - Tempo total (s) | Aleatória - Tempo médio (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| berlin52 | 52 | 7542 | 8980 | 19.07% | 0.000870 | 8181 | 8.47% | 0.039145 | 29772.63 | 1853.97 | 25860 | 242.88% | 0.001544 | 0.051477 |
| kroA100 | 100 | 21282 | 27807 | 30.66% | 0.002720 | 24698 | 16.05% | 0.205024 | 169078.13 | 7226.91 | 155458 | 630.47% | 0.001180 | 0.039323 |
| ch150 | 150 | 6528 | 8191 | 25.47% | 0.003966 | 7113 | 8.96% | 0.636034 | 53936.50 | 1610.64 | 51078 | 682.44% | 0.002529 | 0.084307 |
| kroA200 | 200 | 29368 | 35859 | 22.10% | 0.009177 | 34543 | 17.62% | 1.219765 | 338787.17 | 13294.23 | 314985 | 972.54% | 0.002238 | 0.074603 |

*(Nota: Os valores de GAP foram multiplicados por 100 para representação percentual em relação aos obtidos pela execução original em casas decimais).*

## Passo 5 — Ambiente computacional

Os resultados desta tarefa e da tarefa anterior foram obtidos no seguinte ambiente:
*   **Processador:** 13th Gen Intel(R) Core(TM) i5-13420H (12 núcleos)
*   **Memória RAM:** 16 GB disponível
*   **Sistema operacional:** Windows
*   **Linguagem de programação e bibliotecas:** Python 3.14, utilizando a biblioteca `tsplib95` (v0.7.1) para leitura dos arquivos, e `numpy` e `scipy` para cálculo prático da matriz de distâncias (arredondada para inteiros de acordo com EUC_2D).
*   **Solver (Tarefa 5):** HiGHS (utilizado via `scipy.optimize.milp`).
*   **Uso de threads:** As execuções do solver na tarefa da Aula 5 utilizaram configuração de 1 thread (conforme restrição do roteiro). As heurísticas (vizinho mais próximo e construção aleatória) desta tarefa também foram executadas de forma sequencial (1 thread), permitindo uma comparação justa.

## Passo 6 — Análise

A comparação entre as abordagens revela disparidades claras na qualidade do limite superior (UB). Na tarefa anterior, o solver (MTZ e MCF) alcançou a otimalidade (GAP ~0%) para instâncias menores e deixou GAPs da ordem de 10-15% nas maiores ao atingir o limite de tempo. As heurísticas, em contraste, não chegam tão perto: o Vizinho Mais Próximo Multi-start atingiu GAPs entre 8% e 17.6%. Embora o multi-start apresente uma qualidade razoável e comparável ao que a MTZ conseguiu em 30 minutos na instância de 200 nós, de modo geral, o GAP heurístico é consideravelmente maior que o obtido por métodos exatos, com a construção aleatória gerando GAPs completamente inviáveis (superiores a 200%).

A variante multi-start demonstrou ser um excelente investimento computacional frente ao vizinho mais próximo partindo apenas da cidade 1. O custo de rodar a heurística $n$ vezes aumentou o tempo de execução (indo de ~0.009s para ~1.2s na pior instância), mas esse tempo total ainda é praticamente instantâneo do ponto de vista do usuário. Em contrapartida, a qualidade da solução melhorou drasticamente: o GAP da ch150 caiu de 25.47% para 8.96%, por exemplo. O custo extra compensa amplamente, pois o tempo permanece em uma ordem de grandeza baixíssima enquanto o ganho na rota é significativo.

A heurística de construção aleatória apresentou desvios-padrão altos (ex: ~13294 para kroA200), revelando que há de fato uma forte variabilidade e dependência da sorte em cada execução. Contudo, essa constatação perde força quando comparamos o custo médio da aleatória com o ótimo conhecido: a distância é tão vasta que o espaço amostral de boas soluções é ínfimo. Em outras palavras, mesmo a "melhor" execução entre as 30 sementes ainda resultou em uma rota centenas de vezes pior que o ótimo. A sorte não basta quando o espaço de busca fatorial do TSP cresce; a construção aleatória cega falha em encontrar regiões promissoras por completo.

A diferença na ordem de grandeza dos tempos de execução dita a aplicação prática de cada método. As heurísticas construtivas rodaram em milissegundos a poucos segundos, contra os 1800 segundos (30 minutos) que esgotaram as formulações exatas nas instâncias ch150 e kroA200. Na prática, vale a pena utilizar as heurísticas quando decisões operacionais precisam ser tomadas em tempo real ou quando o tamanho do problema torna a modelagem MCF/MTZ impraticável, servindo também como geração de um limite superior (UB) inicial de boa qualidade para aquecer um solver. O solver, por sua vez, deve ser restrito a casos onde a qualidade impecável da solução compensa a longa e imprevisível espera.
