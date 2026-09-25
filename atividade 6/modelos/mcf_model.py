from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import tsplib95
from scipy import sparse
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.spatial.distance import cdist


def carregar_instancia(arquivo_tsp: str | Path):
    """Carrega e valida o arquivo no formato TSPLIB."""
    caminho = Path(arquivo_tsp)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    problema = tsplib95.load(caminho)
    if problema.type != "TSP":
        raise ValueError(f"Tipo de instância incompatível: {problema.type}")

    return problema


def resolver_tsp_mcf(problema) -> dict:
    """
    Resolve o TSP via formulação MCF (Minimum Cost Flow) usando scipy.milp.

    Variáveis de decisão:
    - x_ij: 1 se a aresta i -> j faz parte da rota, 0 caso contrário
    - f_ij: fluxo associado à aresta i -> j

    Modelo:
    - cada cidade é visitada exatamente uma vez (grau de saída/entrada)
    - o fluxo sai da cidade origem e é consumido nas demais cidades
    - f_ij <= (n - 1) * x_ij para ligar fluxo e decisão binária
    """
    n = problema.dimension
    coords = np.array([problema.node_coords[i] for i in range(1, n + 1)], dtype=float)
    dist = cdist(coords, coords, metric="euclidean")

    num_x = n * n
    num_vars = num_x + num_x

    c = np.zeros(num_vars, dtype=float)
    c[:num_x] = dist.flatten()

    integrality = np.zeros(num_vars, dtype=int)
    integrality[:num_x] = 1

    lb = np.zeros(num_vars, dtype=float)
    ub = np.full(num_vars, np.inf, dtype=float)
    ub[:num_x] = 1.0

    for i in range(n):
        ub[i * n + i] = 0.0

    ub[num_x:] = float(n - 1)

    total_rows = 2 * n + n + (n * n - n)
    A = sparse.dok_matrix((total_rows, num_vars), dtype=float)
    lhs = np.full(total_rows, -np.inf, dtype=float)
    rhs = np.full(total_rows, np.inf, dtype=float)
    row = 0

    # 1. Saída de cada cidade: sum_j x_ij = 1
    for i in range(n):
        for j in range(n):
            A[row, i * n + j] = 1.0
        lhs[row] = rhs[row] = 1.0
        row += 1

    # 2. Entrada de cada cidade: sum_i x_ij = 1
    for j in range(n):
        for i in range(n):
            A[row, i * n + j] = 1.0
        lhs[row] = rhs[row] = 1.0
        row += 1

    # 3. Balanço de fluxo
    # Cidade origem (0): sai n-1 unidades a mais do que entra
    # Demais cidades: consomem 1 unidade a mais do que recebem
    for i in range(n):
        for j in range(n):
            if i != j:
                A[row, num_x + i * n + j] = 1.0
                A[row, num_x + j * n + i] = -1.0
        lhs[row] = rhs[row] = float(n - 1) if i == 0 else -1.0
        row += 1

    # 4. Relaciona fluxo e decisão binária: f_ij <= (n-1) * x_ij
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            A[row, num_x + i * n + j] = 1.0
            A[row, i * n + j] = -(n - 1)
            lhs[row] = -np.inf
            rhs[row] = 0.0
            row += 1

    constraints = LinearConstraint(A.tocsr(), lhs, rhs)

    inicio = time.perf_counter()
    result = milp(
        c=c,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=constraints,
        options={"time_limit": 1800},
    )
    tempo = time.perf_counter() - inicio

    if result.x is None:
        return {
            "rota": None,
            "custo": None,
            "lb": None,
            "ub": None,
            "gap": None,
            "tempo": tempo,
            "status": result.status,
            "message": result.message,
        }

    x_sol = result.x[:num_x].reshape((n, n))
    rota = [0]
    atual = 0
    while len(rota) < n:
        proximo = int(np.argmax(x_sol[atual]))
        if proximo == atual:
            break
        rota.append(proximo)
        atual = proximo
    rota.append(0)

    return {
        "rota": rota,
        "custo": float(result.fun),
        "lb": float(result.mip_dual_bound),
        "ub": float(result.fun),
        "gap": float(result.mip_gap),
        "tempo": tempo,
        "status": result.status,
        "message": result.message,
    }
