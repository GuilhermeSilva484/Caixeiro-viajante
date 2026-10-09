from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELOS_DIR = PROJECT_ROOT / "Modelos"
sys.path.insert(0, str(MODELOS_DIR))

from busca_local_2opt import busca_local_2opt
from construcao_aleatoria import (
    OTIMO_CONHECIDO,
    carregar_instancia_tsp,
    construcao_aleatoria,
)
from vizinho_mais_proximo_multistart import (
    vizinho_mais_proximo,
    vizinho_mais_proximo_multistart,
)


def custo_rota(matriz, rota: list[int]) -> float:
    rota_ciclo = list(rota)
    if len(rota_ciclo) > 1 and rota_ciclo[0] == rota_ciclo[-1]:
        rota_ciclo.pop()
    n = len(rota_ciclo)
    return float(
        sum(
            matriz[rota_ciclo[i] - 1, rota_ciclo[(i + 1) % n] - 1]
            for i in range(n)
        )
    )


def formatar_gap(custo: float, otimo: float | None) -> str:
    if otimo is None:
        return "N/A"
    return f"{(custo - otimo) / otimo * 100:.2f}%"


def main() -> None:
    arquivos_tsp = sorted((PROJECT_ROOT / "dados").glob("*.tsp"))
    if not arquivos_tsp:
        raise FileNotFoundError(f"Nenhum arquivo .tsp encontrado em {PROJECT_ROOT / 'dados'}.")

    linhas = []
    linhas_auxiliares = []
    for arquivo_tsp in arquivos_tsp:
        matriz = carregar_instancia_tsp(arquivo_tsp)
        n = matriz.shape[0]
        otimo = OTIMO_CONHECIDO.get(arquivo_tsp.name)

        nn_inicial = vizinho_mais_proximo(matriz, 1)
        nn_final = busca_local_2opt(matriz, nn_inicial["rota"])

        multi_inicial = vizinho_mais_proximo_multistart(matriz)
        multi_final = busca_local_2opt(matriz, multi_inicial["rota"])

        custos_aleatorios_antes = []
        custos_aleatorios_depois = []
        melhorias_aleatorias = []
        inversoes_aleatorias = []
        tempos_2opt_aleatorios = []
        for seed in range(30):
            resultado_inicial = construcao_aleatoria(matriz, seed=seed)
            resultado_final = busca_local_2opt(matriz, resultado_inicial["rota"])
            custos_aleatorios_antes.append(resultado_inicial["custo"])
            custos_aleatorios_depois.append(resultado_final["custo"])
            melhorias_aleatorias.append(
                (resultado_inicial["custo"] - resultado_final["custo"])
                / resultado_inicial["custo"]
                * 100
            )
            inversoes_aleatorias.append(resultado_final["inversoes"])
            tempos_2opt_aleatorios.append(resultado_final["tempo"])

        custo_medio_antes = sum(custos_aleatorios_antes) / len(custos_aleatorios_antes)
        custo_medio_depois = sum(custos_aleatorios_depois) / len(custos_aleatorios_depois)
        desvio_antes = (
            sum((custo - custo_medio_antes) ** 2 for custo in custos_aleatorios_antes)
            / len(custos_aleatorios_antes)
        ) ** 0.5
        desvio_depois = (
            sum((custo - custo_medio_depois) ** 2 for custo in custos_aleatorios_depois)
            / len(custos_aleatorios_depois)
        ) ** 0.5
        melhor_antes = min(custos_aleatorios_antes)
        melhor_depois = min(custos_aleatorios_depois)
        custo_nn = custo_rota(matriz, nn_inicial["rota"])
        custo_multi = custo_rota(matriz, multi_inicial["rota"])
        tempo_medio_aleatorio = sum(tempos_2opt_aleatorios) / len(tempos_2opt_aleatorios)
        inversoes_media = sum(inversoes_aleatorias) / len(inversoes_aleatorias)

        resultados = [
            ("NN cidade 1", custo_nn, nn_final["custo"], nn_final["inversoes"], nn_final["tempo"]),
            (
                "NN multi-start",
                custo_multi,
                multi_final["custo"],
                multi_final["inversoes"],
                multi_final["tempo"],
            ),
        ]
        for heuristica, custo_inicial, custo_final, inversoes, tempo in resultados:
            melhoria = (custo_inicial - custo_final) / custo_inicial * 100
            linhas.append(
                f"| {arquivo_tsp.stem} | {n} | {otimo or 'N/A'} | {heuristica} | "
                f"{custo_inicial:.2f} | {formatar_gap(custo_inicial, otimo)} | "
                f"{custo_final:.2f} | {formatar_gap(custo_final, otimo)} | "
                f"{melhoria:.2f}% | {inversoes} | {tempo:.6f} |"
            )

        melhoria_media = sum(melhorias_aleatorias) / len(melhorias_aleatorias)
        linhas.append(
            f"| {arquivo_tsp.stem} | {n} | {otimo or 'N/A'} | Aleatória (30) | "
            f"{custo_medio_antes:.2f} | {formatar_gap(custo_medio_antes, otimo)} | "
            f"{custo_medio_depois:.2f} | {formatar_gap(custo_medio_depois, otimo)} | "
            f"{melhoria_media:.2f}% | {inversoes_media:.1f} | "
            f"{tempo_medio_aleatorio:.6f} |"
        )
        linhas_auxiliares.append(
            f"| {arquivo_tsp.stem} | {otimo or 'N/A'} | {custo_medio_antes:.2f} | "
            f"{desvio_antes:.2f} | {melhor_antes:.2f} | {formatar_gap(melhor_antes, otimo)} | "
            f"{custo_medio_depois:.2f} | {desvio_depois:.2f} | {melhor_depois:.2f} | "
            f"{formatar_gap(melhor_depois, otimo)} |"
        )

    print(
        "| Instância | n | Ótimo | Heurística | Custo inicial | GAP inicial | "
        "Custo após 2-opt | GAP após 2-opt | Melhoria | Inversões feitas | Tempo do 2-opt (s) |"
    )
    print(
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|"
    )
    print("\n".join(linhas))
    print("\nTabela auxiliar: heurística aleatória com 2-opt (30 execuções)")
    print(
        "| Instância | Ótimo | Antes: média | Antes: desvio-padrão | Antes: melhor | "
        "GAP do melhor (antes) | Depois: média | Depois: desvio-padrão | "
        "Depois: melhor | GAP do melhor (depois) |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    print("\n".join(linhas_auxiliares))


if __name__ == "__main__":
    main()