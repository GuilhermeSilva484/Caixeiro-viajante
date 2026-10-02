from __future__ import annotations#Permite o uso de anotações de tipo avançadas, como tipos de retornos de função que ainda não foram declarados, melhorando a legibilidade e a manutenção do código.
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


def resolver_tsp_mtz(problema) -> dict:
    """
    Resolve o TSP via formulação MTZ (Miller-Tucker-Zemlin) usando scipy.milp.
    """
    n = problema.dimension
    coords = np.array([problema.node_coords[i] for i in range(1, n + 1)], dtype=float)
    dist = cdist(coords, coords, metric="euclidean")

    num_x = n * n
    num_vars = num_x + n  # n*n variáveis x + n variáveis u

    # 1. Função Objetivo
    c = np.zeros(num_vars)
    c[:num_x] = dist.flatten()

    # 2. Tipos e Limites das Variáveis
    integrality = np.zeros(num_vars)
    integrality[:num_x] = 1  # Variáveis binárias para x_ij

    lb = np.zeros(num_vars)
    ub = np.full(num_vars, np.inf)

    ub[:num_x] = 1.0
    for i in range(n):
        ub[i * n + i] = 0.0  # Impede x_ii = 1

    for i in range(1, n):
        lb[num_x + i] = 2.0
        ub[num_x + i] = float(n)

    # 3. Restrições Lineares
    A = sparse.dok_matrix((2 * n + (n - 1) * (n - 2), num_vars), dtype=float)
    lhs, rhs = [], []
    row = 0

    # Restrição de Saída
    for i in range(n):
        for j in range(n):
            A[row, i * n + j] = 1.0
        lhs.append(1.0)
        rhs.append(1.0)
        row += 1

    # Restrição de Entrada
    for j in range(n):
        for i in range(n):
            A[row, i * n + j] = 1.0
        lhs.append(1.0)
        rhs.append(1.0)
        row += 1

    # Eliminação de Subrotas (MTZ)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                A[row, num_x + i] = 1.0
                A[row, num_x + j] = -1.0
                A[row, i * n + j] = float(n)
                lhs.append(-np.inf)
                rhs.append(float(n - 1))
                row += 1

    constraints = LinearConstraint(A.tocsr(), lhs, rhs)

    # 4. Execução do Solver HiGHS
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

    # 5. Reconstrução da Rota
    x_sol = result.x[:num_x].reshape((n, n))
    rota = [0]
    atual = 0
    while len(rota) < n:
        proximo = int(np.argmax(x_sol[atual]))
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
