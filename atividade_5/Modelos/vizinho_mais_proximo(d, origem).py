from __future__ import annotations
import numpy as np
from time import perf_counter

def vizinho_mais_proximo(d, origem: int = 1, otimo_conhecido: float | None = None) -> dict:
    inicio = perf_counter()
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

    res = {
        "cidade_origem": origem,
        "custo": float(custo_total),
        "rota": rota,
        "tempo": perf_counter() - inicio,
    }

    if otimo_conhecido is not None and otimo_conhecido > 0:
        gap = (custo_total - otimo_conhecido) / otimo_conhecido
        res["gap"] = float(gap)

    return res


def vizinho_mais_proximo_multistart(
    d, otimo_conhecido: float | None = None
) -> dict:
    inicio = perf_counter()
    matriz = np.array(d, dtype=float)
    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ValueError("d deve ser uma matriz quadrada de distâncias.")
    if matriz.shape[0] == 0:
        raise ValueError("d deve conter pelo menos uma cidade.")

    resultados = [
        vizinho_mais_proximo(matriz, origem, otimo_conhecido)
        for origem in range(1, matriz.shape[0] + 1)
    ]
    melhor = dict(min(resultados, key=lambda resultado: resultado["custo"]))
    melhor["tempo"] = perf_counter() - inicio
    melhor["multistart"] = True
    return melhor


if __name__ == "__main__":
    # Matriz de distâncias de exemplo
    dist = np.array(
        [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0],
        ]
    )
    
    # Ótimo conhecido da instância (substitua pelo valor real da instância, ex: 7542 para berlin52)
    otimo_exemplo = 80.0

    # Executa partindo da Cidade 1
    resultado = vizinho_mais_proximo(dist, origem=1, otimo_conhecido=otimo_exemplo)
    resultado_multistart = vizinho_mais_proximo_multistart(
        dist, otimo_conhecido=otimo_exemplo
    )

    # Exibição formatada dos resultados
    print("=" * 35)
    print("  VIZINHO MAIS PRÓXIMO (CIDADE 1)")
    print("=" * 35)
    print(f"  Cidade de Origem : Cidade {resultado['cidade_origem']}")
    print(f"  Custo Total      : {resultado['custo']:.2f}")
    print(f"  Tempo (s)        : {resultado['tempo']:.6f}")
    print(f"  Rota             : {resultado['rota']}")
    if "gap" in resultado:
        print(f"  GAP              : {resultado['gap']:.6f} ({resultado['gap'] * 100:.2f}%)")
    print("=" * 35)
    print("  MULTISTART")
    print(f"  Cidade de Origem : Cidade {resultado_multistart['cidade_origem']}")
    print(f"  Custo Total      : {resultado_multistart['custo']:.2f}")
    print(f"  Tempo (s)        : {resultado_multistart['tempo']:.6f}")
    print(f"  Rota             : {resultado_multistart['rota']}")