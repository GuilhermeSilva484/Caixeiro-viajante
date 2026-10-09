# Tarefa Avaliativa — Busca Local 2-opt para o TSP

## Passo 4 — Tabela de Resultados

| Instância | n | Ótimo | Heurística | Custo inicial | GAP inicial | Custo após 2-opt | GAP após 2-opt | Melhoria (%) | Inversões feitas | Tempo do 2-opt (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| berlin52 | 52 | 7542.0 | NN cidade 1 | 8980.92 | 19.08% | 8061.69 | 6.89% | 10.24% | 16 | 0.007235 |
| berlin52 | 52 | 7542.0 | NN multi-start | 8182.19 | 8.49% | 7723.70 | 2.41% | 5.60% | 13 | 0.003966 |
| berlin52 | 52 | 7542.0 | Aleatória | 29773.85 | 294.77% | 8398.00 | 11.35% | 71.68% | 187.8 | 0.037984 |
| kroA100 | 100 | 21282.0 | NN cidade 1 | 26856.39 | 26.19% | 22314.46 | 4.85% | 16.91% | 45 | 0.029631 |
| kroA100 | 100 | 21282.0 | NN multi-start | 24698.50 | 16.05% | 21569.45 | 1.35% | 12.67% | 28 | 0.023802 |
| kroA100 | 100 | 21282.0 | Aleatória | 169077.79 | 694.46% | 24149.86 | 13.48% | 85.69% | 463.9 | 0.239805 |
| ch150 | 150 | 6528.0 | NN cidade 1 | 8194.61 | 25.53% | 6986.94 | 7.03% | 14.74% | 57 | 0.143948 |
| ch150 | 150 | 6528.0 | NN multi-start | 7078.44 | 8.43% | 6733.74 | 3.15% | 4.87% | 24 | 0.048376 |
| ch150 | 150 | 6528.0 | Aleatória | 53937.15 | 726.24% | 7443.51 | 14.02% | 86.19% | 715.7 | 0.681045 |
| kroA200 | 200 | 29368.0 | NN cidade 1 | 35798.41 | 21.90% | 30405.86 | 3.53% | 15.06% | 89 | 0.203987 |
| kroA200 | 200 | 29368.0 | NN multi-start | 34547.69 | 17.64% | 30992.97 | 5.53% | 10.29% | 44 | 0.122511 |
| kroA200 | 200 | 29368.0 | Aleatória | 338787.70 | 1053.59% | 33314.41 | 13.44% | 90.15% | 1116.7 | 1.765050 |

### Tabela Auxiliar — Heurística Aleatória com 2-opt (30 execuções)

| Instância | Ótimo | Antes: média | Antes: desvio-padrão | Antes: melhor | GAP do melhor (antes) | Depois: média | Depois: desvio-padrão | Depois: melhor | GAP do melhor (depois) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| berlin52 | 7542.0 | 29773.85 | 1822.87 | 25859.06 | 242.87% | 8398.00 | 251.29 | 8045.66 | 6.68% |
| kroA100 | 21282.0 | 169077.79 | 7105.03 | 155457.33 | 630.46% | 24149.86 | 741.70 | 22410.31 | 5.30% |
| ch150 | 6528.0 | 53937.15 | 1583.03 | 51081.99 | 682.51% | 7443.51 | 241.03 | 6971.65 | 6.80% |
| kroA200 | 29368.0 | 338787.70 | 13070.09 | 314988.13 | 972.56% | 33314.41 | 797.37 | 31788.48 | 8.24% |

---

## Passo 5 — Ambiente Computacional

Os testes foram executados no seguinte ambiente:
* **Processador:** 2-core virtual CPU
* **Memória RAM:** 8 GB
* **Sistema Operacional:** Máquina virtual Linux (Ubuntu) no GitHub Codespaces
* **Linguagem de Programação:** Python 3.14.2
* **Execução:** Sequencial (1 thread).

---

## Passo 6 — Análise

A busca local 2-opt reduziu substancialmente o custo final de todas as abordagens. A heurística de construção Aleatória foi a mais beneficiada em termos relativos, alcançando taxas de melhoria vertiginosas que variaram de 71,68% na instância berlin52 a 90,15% na kroA200. Em contrapartida, as heurísticas baseadas no Vizinho Mais Próximo (NN cidade 1 e NN multi-start) apresentaram ganhos percentuais menores (entre 4,87% e 16,91%) exatamente porque já partiam de rotas iniciais de boa qualidade anatômica, com GAPs iniciais substancialmente menores.

Apesar da recuperação impressionante promovida pelo 2-opt sobre rotas aleatórias, a qualidade da solução inicial continua sendo um fator determinante no resultado final. Na instância kroA100, por exemplo, a rota aleatória melhorada estacionou num GAP médio de 13,48%, enquanto o NN multi-start atingiu um GAP final de apenas 1,35%. Isso evidencia que fornecer um ponto de partida superior ajuda o algoritmo de busca local a convergir para ótimos locais de muito melhor qualidade, não diluindo a vantagem de se utilizar uma heurística construtiva refinada.

O facto de as soluções finais manterem um GAP não nulo (como os 3,15% observados no NN multi-start para a ch150) ocorre porque o 2-opt encerra a sua execução assim que atinge um ótimo local em relação à sua própria vizinhança. Nesse ponto, não existe nenhuma remoção e inversão de duas arestas capaz de diminuir o custo da rota. O algoritmo fica restrito num "vale" do espaço de busca; para se aproximar do ótimo global conhecido, seria necessário utilizar um movimento que rearranjasse trechos maiores e mais complexos simultaneamente, como nas vizinhanças 3-opt ou 4-opt.

Por fim, o custo computacional da implementação da busca local mostrou-se altamente rentável face aos ganhos de qualidade. O número de inversões e o tempo de processamento crescem à medida que o tamanho da instância $n$ aumenta: na heurística Aleatória, saltou-se de 187,8 inversões na berlin52 para 1116,7 na kroA200, consumindo em média 1,765 segundos. Para o NN multi-start, a mesma instância kroA200 foi resolvida em rápidos 0,122 segundos. Este acréscimo temporal de frações de segundo compensa vastamente a redução do GAP entregue pelo algoritmo.
