from __future__ import annotations

import math
import random
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


def construcao_aleatoria(d, seed=None):
    matriz = np.array(d, dtype=float)

    if matriz.ndim != 2 or matriz.shape[0] != matriz.shape[1]:
        raise ValueError("d deve ser uma matriz quadrada de distâncias.")

    n = matriz.shape[0]
    rng = random.Random(seed)
    rota = list(range(1, n + 1))
    rng.shuffle(rota)

    custo_total = 0.0
    for i in range(n):
        atual = rota[i] - 1
        proximo = rota[(i + 1) % n] - 1
        custo_total += matriz[atual, proximo]

    return {"rota": rota, "custo": float(custo_total)}


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


def rodar_30_vezes(caminho_arquivo: str | Path):
    matriz = carregar_instancia_tsp(caminho_arquivo)
    nome = Path(caminho_arquivo).name
    custos = []
    tempos = []

    for seed in range(30):
        inicio = time.perf_counter()
        resultado = construcao_aleatoria(matriz, seed=seed)
        tempo = time.perf_counter() - inicio
        custos.append(resultado["custo"])
        tempos.append(tempo)

    custo_min = min(custos)
    custo_max = max(custos)
    custo_medio = sum(custos) / len(custos)
    tempo_total = sum(tempos)
    tempo_medio = tempo_total / len(tempos)
    desvio_padrao = math.sqrt(sum((c - custo_medio) ** 2 for c in custos) / len(custos))
    otimo = OTIMO_CONHECIDO.get(nome)
    gap_medio = None if otimo is None else ((custo_medio - otimo) / otimo) * 100.0
    melhor_custo = custo_min

    return {
        "instancia": nome,
        "cidades": matriz.shape[0],
        "otimo": otimo,
        "custo_medio": custo_medio,
        "desvio_padrao": desvio_padrao,
        "melhor_custo": melhor_custo,
        "gap_medio": gap_medio,
        "tempo_total": tempo_total,
        "tempo_medio": tempo_medio,
    }


def executar_para_todas_instancias(diretorio_dados: str | Path | None = None):
    base = Path(__file__).resolve().parents[1]
    pasta_dados = Path(diretorio_dados) if diretorio_dados is not None else base / "dados"

    arquivos_tsp = sorted(pasta_dados.glob("*.tsp"))
    if not arquivos_tsp:
        raise FileNotFoundError(f"Nenhum arquivo .tsp encontrado em {pasta_dados}.")

    return [rodar_30_vezes(arquivo) for arquivo in arquivos_tsp]


if __name__ == "__main__":
    print(
        "Instância | Cidades | Ótimo conhecido | Custo médio | Desvio padrão | Melhor custo | Gap (%) | Tempo total (s) | Tempo médio (s)"
    )
    for item in executar_para_todas_instancias():
        otimo = "N/A" if item["otimo"] is None else f"{item['otimo']:.2f}"
        gap = "N/A" if item["gap_medio"] is None else f"{item['gap_medio']:.2f}"
        print(
            f"{item['instancia']} | {item['cidades']} | {otimo} | {item['custo_medio']:.2f} | "
            f"{item['desvio_padrao']:.2f} | {item['melhor_custo']:.2f} | {gap} | {item['tempo_total']:.6f} | {item['tempo_medio']:.6f}"
        )
