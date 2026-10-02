# pyrefly: ignore [missing-import]
import tsplib95
import numpy as np
import time
import random
import statistics
from pathlib import Path
from scipy.spatial.distance import cdist

def ler_instancia(arquivo_tsp):
    """
    Lê uma instância TSPLIB e retorna a quantidade de cidades n e a 
    matriz de distâncias d (EUC_2D arredondada para o inteiro mais próximo).
    """
    problema = tsplib95.load(arquivo_tsp)
    n = problema.dimension
    coords = np.array([problema.node_coords[i] for i in range(1, n + 1)], dtype=float)
    # Distância Euclidiana 2D arredondada para o inteiro mais próximo
    dist = np.round(cdist(coords, coords, metric="euclidean")).astype(int)
    return n, dist

def vizinho_mais_proximo(d, origem):
    n = len(d)
    visitados = [False] * n
    rota = [origem]
    visitados[origem] = True
    custo = 0
    atual = origem
    
    inicio = time.perf_counter()
    for _ in range(n - 1):
        min_dist = float('inf')
        proximo = -1
        for j in range(n):
            if not visitados[j] and d[atual][j] < min_dist:
                min_dist = d[atual][j]
                proximo = j
        rota.append(proximo)
        visitados[proximo] = True
        custo += min_dist
        atual = proximo
    
    custo += d[atual][origem]
    rota.append(origem)
    
    tempo_exec = time.perf_counter() - inicio
    return rota, custo, tempo_exec

def vizinho_mais_proximo_multistart(d):
    n = len(d)
    melhor_custo = float('inf')
    melhor_rota = None
    
    inicio = time.perf_counter()
    for origem in range(n):
        visitados = [False] * n
        rota = [origem]
        visitados[origem] = True
        custo = 0
        atual = origem
        
        for _ in range(n - 1):
            min_dist = float('inf')
            proximo = -1
            for j in range(n):
                if not visitados[j] and d[atual][j] < min_dist:
                    min_dist = d[atual][j]
                    proximo = j
            rota.append(proximo)
            visitados[proximo] = True
            custo += min_dist
            atual = proximo
        
        custo += d[atual][origem]
        rota.append(origem)
        
        if custo < melhor_custo:
            melhor_custo = custo
            melhor_rota = rota
            
    tempo_exec = time.perf_counter() - inicio
    return melhor_rota, melhor_custo, tempo_exec

def construcao_aleatoria(d, seed):
    n = len(d)
    random.seed(seed)
    
    inicio = time.perf_counter()
    cidades = list(range(n))
    random.shuffle(cidades)
    
    custo = 0
    for i in range(n - 1):
        custo += d[cidades[i]][cidades[i+1]]
    custo += d[cidades[-1]][cidades[0]]
    
    rota = cidades + [cidades[0]]
    tempo_exec = time.perf_counter() - inicio
    return rota, custo, tempo_exec

def main():
    base = Path(__file__).resolve().parents[1]
    arquivos = {
        "berlin52": (base / "atividade_5" / "dados" / "berlin52.tsp", 7542),
        "kroA100": (base / "atividade_5" / "dados" / "kroA100.tsp", 21282),
        "ch150": (base / "atividade_5" / "dados" / "ch150.tsp", 6528),
        "kroA200": (base / "atividade_5" / "dados" / "kroA200.tsp", 29368),
    }

    # Header da tabela
    print("| Instância | Cidades (n) | Ótimo conhecido | NN cidade 1 - Custo | NN cidade 1 - GAP | NN cidade 1 - Tempo (s) | NN multi-start - Custo | NN multi-start - GAP | NN multi-start - Tempo (s) | Aleatória - Custo médio | Aleatória - Desvio padrão | Aleatória - Melhor custo | Aleatória - GAP (melhor) | Aleatória - Tempo total (s) | Aleatória - Tempo médio (ms) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    for nome_instancia, (caminho_tsp, otimo_conhecido) in arquivos.items():
        if not caminho_tsp.exists():
            print(f"ERRO: Arquivo não encontrado: {caminho_tsp}")
            continue
            
        n, d = ler_instancia(caminho_tsp)
        
        # 1. NN cidade 1
        _, custo_nn1, tempo_nn1 = vizinho_mais_proximo(d, 0)
        gap_nn1 = (custo_nn1 - otimo_conhecido) / otimo_conhecido
        
        # 2. NN multi-start
        _, custo_nn_multi, tempo_nn_multi = vizinho_mais_proximo_multistart(d)
        gap_nn_multi = (custo_nn_multi - otimo_conhecido) / otimo_conhecido
        
        # 3. Aleatória (30 seeds)
        custos_aleatoria = []
        tempo_total_aleatoria = 0.0
        melhor_custo_aleatoria = float('inf')
        
        for i in range(30):
            # Usando sementes fixas para reprodutibilidade se desejar (ex: i)
            _, c_al, t_al = construcao_aleatoria(d, seed=i)
            custos_aleatoria.append(float(c_al))
            tempo_total_aleatoria += t_al
            if c_al < melhor_custo_aleatoria:
                melhor_custo_aleatoria = c_al
                
        custo_medio_al = statistics.mean(custos_aleatoria)
        desvio_al = statistics.stdev(custos_aleatoria)
        gap_melhor_al = (melhor_custo_aleatoria - otimo_conhecido) / otimo_conhecido
        tempo_medio_al_ms = (tempo_total_aleatoria / 30.0) * 1000.0
        
        print(f"| {nome_instancia} | {n} | {otimo_conhecido} | {custo_nn1} | {gap_nn1:.4f} | {tempo_nn1:.6f} | {custo_nn_multi} | {gap_nn_multi:.4f} | {tempo_nn_multi:.6f} | {custo_medio_al:.2f} | {desvio_al:.2f} | {melhor_custo_aleatoria} | {gap_melhor_al:.4f} | {tempo_total_aleatoria:.6f} | {tempo_medio_al_ms:.6f} |")

if __name__ == "__main__":
    main()
