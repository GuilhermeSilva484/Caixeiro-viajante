from __future__ import annotations
from pathlib import Path

import numpy as np

def vizinho_mais_proximo(d, origem: int = 1, otimo_conhecido: float | None = None) -> dict:
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
        "rota": rota
    }

    if otimo_conhecido is not None and otimo_conhecido > 0:
        gap = (custo_total - otimo_conhecido) / otimo_conhecido
        res["gap"] = float(gap)

    return res


def matriz_da_instancia(arquivo_tsp: str | Path) -> np.ndarray:
    linhas = Path(arquivo_tsp).read_text(encoding="utf-8").splitlines()
    inicio = linhas.index("NODE_COORD_SECTION") + 1
    coordenadas = []
    for linha in linhas[inicio:]:
        if linha.strip() == "EOF":
            break
        partes = linha.split()
        if len(partes) >= 3:
            coordenadas.append((float(partes[1]), float(partes[2])))

    if not coordenadas:
        raise ValueError(f"Nenhuma coordenada encontrada em {arquivo_tsp}.")

    coordenadas = np.array(coordenadas, dtype=float)
    diferencas = coordenadas[:, np.newaxis, :] - coordenadas[np.newaxis, :, :]
    return np.sqrt(np.sum(diferencas**2, axis=2))


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1] / "dados"
    instancias = ["berlin52", "ch150", "dj38", "kroA100", "kroA200"]

    print("instancia | cidades | custo | rota")
    for nome in instancias:
        matriz = matriz_da_instancia(base / f"{nome}.tsp")
        resultado = vizinho_mais_proximo(matriz, origem=1)
        rota = " -> ".join(map(str, resultado["rota"]))
        print(f"{nome} | {matriz.shape[0]} | {resultado['custo']:.2f} | {rota}\n")