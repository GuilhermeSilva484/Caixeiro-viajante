from __future__ import annotations
import math
import time
import numpy as np

def busca_local_2opt(d, rota):
    inicio = time.perf_counter()
    matriz = np.array(d, dtype=float)
    n = len(rota)
    custo_inicial = sum(
        matriz[rota[i] - 1, rota[(i + 1) % n] - 1] for i in range(n)
    )
    custo = float(custo_inicial)
    inversoes = 0
    print(f"Custo inicial: {custo_inicial}")
    while True:
        movimento_encontrado = False
        arestas_examinadas = set()

        for k in range(2, n - 1):
            for inicio_trecho in range(n - k + 1):
                fim_trecho = inicio_trecho + k - 1
                aresta_anterior = (inicio_trecho - 1) % n
                aresta_posterior = fim_trecho
                chave = tuple(sorted((aresta_anterior, aresta_posterior)))
                if chave in arestas_examinadas:
                    continue
                arestas_examinadas.add(chave)

                a = rota[aresta_anterior] - 1
                b = rota[inicio_trecho] - 1
                c = rota[fim_trecho] - 1
                d_proximo = rota[(fim_trecho + 1) % n] - 1
                delta = (
                    matriz[a, c]
                    + matriz[b, d_proximo]
                    - matriz[a, b]
                    - matriz[c, d_proximo]
                )

                if delta < 0:
                    rota[inicio_trecho : fim_trecho + 1] = reversed(
                        rota[inicio_trecho : fim_trecho + 1]
                    )
                    custo += float(delta)
                    inversoes += 1
                    movimento_encontrado = True
                    break

            if movimento_encontrado:
                break

        if not movimento_encontrado:
            break

    custo_recalculado = sum(
        matriz[rota[i] - 1, rota[(i + 1) % n] - 1] for i in range(n)
    )
    return {
        "rota": rota,
        "custo": float(custo),
        "inversoes": inversoes,
        "tempo": time.perf_counter() - inicio,
    }
