from __future__ import annotations
import math
import time
import numpy as np

def busca_local_2opt(d, rota):
    inicio = time.perf_counter()
    matriz = np.array(d, dtype=float)
    rota = list(rota)
    if len(rota) > 1 and rota[0] == rota[-1]:
        rota.pop()
    n = len(rota)
    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ValueError("d deve ser uma matriz quadrada de distâncias.")
    if n != matriz.shape[0] or len(set(rota)) != n:
        raise ValueError("rota deve ser uma permutação das cidades da matriz.")
    if any(cidade < 1 or cidade > n for cidade in rota):
        raise ValueError("rota deve conter índices de cidade entre 1 e n.")
    cidade_inicial = rota[0]

    custo_inicial = sum(
        matriz[rota[i] - 1, rota[(i + 1) % n] - 1] for i in range(n)
    )
    custo = float(custo_inicial)
    inversoes = 0

    while True:
        movimento_encontrado = False
        movimentos_examinados = set()
        for k in range(2, n - 1):
            for inicio_trecho in range(n):
                fim_trecho = (inicio_trecho + k - 1) % n
                aresta_anterior = (inicio_trecho - 1) % n
                aresta_posterior = fim_trecho
                chave = tuple(sorted((aresta_anterior, aresta_posterior)))
                if chave in movimentos_examinados:
                    continue
                movimentos_examinados.add(chave)

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
                    indices_trecho = [(inicio_trecho + i) % n for i in range(k)]
                    cidades_invertidas = [rota[indice] for indice in indices_trecho][::-1]
                    for indice, cidade in zip(indices_trecho, cidades_invertidas):
                        rota[indice] = cidade
                    custo += float(delta)
                    inversoes += 1
                    movimento_encontrado = True
                    break

            if movimento_encontrado:
                break

        if not movimento_encontrado:
            break

    indice_inicial = rota.index(cidade_inicial)
    rota = rota[indice_inicial:] + rota[:indice_inicial]
    custo_recalculado = sum(
        matriz[rota[i] - 1, rota[(i + 1) % n] - 1] for i in range(n)
    )
    if not math.isclose(custo, custo_recalculado, rel_tol=1e-9, abs_tol=1e-9):
        raise AssertionError("O custo acumulado não coincide com o custo da rota final.")

    return {
        "rota": rota,
        "custo": float(custo),
        "inversoes": inversoes,
        "tempo": time.perf_counter() - inicio,
    }
