from __future__ import annotations
import numpy as np

def vizinho_mais_proximo(d, origem):
    matriz = np.array(d, dtype=float)

    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ValueError("d deve ser uma matriz quadrada de distâncias.")

    n = matriz.shape[0]
    if not 1 <= origem <= n:
        raise ValueError(f"origem deve estar entre 1 e {n}.")

    origem_idx = origem - 1
    visitados = {origem_idx}
    rota = [origem]
    atual = origem_idx
    custo_total = 0.0

    while len(visitados) < n:
        candidatos = [i for i in range(n) if i not in visitados]
        proximo = min(candidatos, key=lambda j: matriz[atual, j])

        custo_total += matriz[atual, proximo]
        visita = proximo + 1
        rota.append(visita)
        visitados.add(proximo)
        atual = proximo

    custo_total += matriz[atual, origem_idx]
    rota.append(origem)

    return {"rota": rota, "custo": float(custo_total)}


if __name__ == "__main__":
    dist = np.array(
        [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0],
        ]
    )
    resultado = vizinho_mais_proximo(dist, 1)
    print(resultado)
