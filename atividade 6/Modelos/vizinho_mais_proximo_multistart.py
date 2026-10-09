from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np

OTIMO_CONHECIDO = {
    "berlin52.tsp": 7542.0,
    "ch150.tsp": 6528.0,
    "dj38.tsp": 6656.0,
    "kroA100.tsp": 21282.0,
    "kroA200.tsp": 29368.0,
}


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
        rota.append(proximo + 1)
        visitados.add(proximo)
        atual = proximo

    custo_total += matriz[atual, origem_idx]
    rota.append(origem)

    return {"rota": rota, "custo": float(custo_total)}


def vizinho_mais_proximo_multistart(d, origens=None):
    matriz = np.array(d, dtype=float)
    n = matriz.shape[0]

    if origens is None:
        origens = list(range(1, n + 1))

    melhor_rota = None
    melhor_custo = float("inf")

    for origem in origens:
        if not 1 <= origem <= n:
            continue
        resultado = vizinho_mais_proximo(matriz, origem)
        if resultado["custo"] < melhor_custo:
            melhor_custo = resultado["custo"]
            melhor_rota = resultado

    if melhor_rota is None:
        raise ValueError("Nenhuma origem válida foi fornecida para o multi-start.")

    return melhor_rota


def carregar_instancia_tsp(caminho_arquivo: str | Path):
    caminho = Path(caminho_arquivo)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    coordenadas = {}
    lendo_coordenadas = False

    with caminho.open("r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            texto = linha.strip()
            if not texto:
                continue

            if texto.upper().startswith("NODE_COORD_SECTION"):
                lendo_coordenadas = True
                continue

            if not lendo_coordenadas:
                continue

            if texto.upper().startswith("EOF"):
                break

            partes = texto.split()
            if len(partes) < 3:
                continue

            indice = int(partes[0])
            x = float(partes[1])
            y = float(partes[2])
            coordenadas[indice] = (x, y)

    if not coordenadas:
        raise ValueError(f"Nenhuma coordenada encontrada em {caminho.name}.")

    indices = sorted(coordenadas)
    n = len(indices)
    matriz = np.zeros((n, n), dtype=float)

    for i in range(n):
        xi, yi = coordenadas[indices[i]]
        for j in range(n):
            xj, yj = coordenadas[indices[j]]
            matriz[i, j] = math.hypot(xj - xi, yj - yi)

    return matriz


def executar_para_todas_instancias(diretorio_dados: str | Path | None = None):
    base = Path(__file__).resolve().parents[1]
    pasta_dados = Path(diretorio_dados) if diretorio_dados is not None else base / "dados"

    arquivos_tsp = sorted(pasta_dados.glob("*.tsp"))
    if not arquivos_tsp:
        raise FileNotFoundError(f"Nenhum arquivo .tsp encontrado em {pasta_dados}.")

    resultados = []
    for arquivo in arquivos_tsp:
        inicio = time.perf_counter()
        matriz = carregar_instancia_tsp(arquivo)
        resultado = vizinho_mais_proximo_multistart(matriz, list(range(1, matriz.shape[0] + 1)))
        tempo = time.perf_counter() - inicio

        nome_instancia = arquivo.name
        n = matriz.shape[0]
        otimo = OTIMO_CONHECIDO.get(nome_instancia)
        custo = resultado["custo"]
        gap = None if otimo is None else ((custo - otimo) / otimo) * 100.0

        resultados.append(
            {
                "arquivo": nome_instancia,
                "cidades": n,
                "otimo": otimo,
                "custo": custo,
                "gap": gap,
                "tempo": tempo,
                "rota": resultado["rota"],
            }
        )

    return resultados


if __name__ == "__main__":
    print("Instância | Cidades | Ótimo conhecido | Custo | Gap (%) | Tempo (s)")
    for item in executar_para_todas_instancias():
        otimo = "N/A" if item["otimo"] is None else f"{item['otimo']:.2f}"
        gap = "N/A" if item["gap"] is None else f"{item['gap']:.2f}"
        print(
            f"{item['arquivo']} | {item['cidades']} | {otimo} | {item['custo']:.2f} | {gap} | {item['tempo']:.6f}"
        )
