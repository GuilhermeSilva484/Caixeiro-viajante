from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modelos.mcf_model import carregar_instancia, resolver_tsp_mcf
from modelos.mtz_model import carregar_instancia as carregar_instancia_mtz
from modelos.mtz_model import resolver_tsp_mtz


def print_result(problema, formulacao: str, res: dict) -> None:
    lb = "N/A" if res["lb"] is None else f"{res['lb']:.2f}"
    ub = "N/A" if res["ub"] is None else f"{res['ub']:.2f}"
    gap = "N/A" if res["gap"] is None else f"{res['gap']:.6f}"
    print(
        f"{problema.name} | {problema.dimension} | {formulacao} | HiGHS | "
        f"{lb} | {ub} | {gap} | {res['tempo']:.4f} | {res['status']} ({res['message']})"
    )


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    arquivos_tsp = [
        base / "dados" / "berlin52.tsp",
        base / "dados" / "ch150.tsp",
        base / "dados" / "dj38.tsp",
        base / "dados" / "kroA100.tsp",
        base / "dados" / "kroA200.tsp",
    ]

    for arquivo_tsp in arquivos_tsp:
        print(f"\n===== Teste: {arquivo_tsp.name} =====")
        try:
            problema = carregar_instancia(arquivo_tsp)
            print("instancia | cidade n | Formulação | solver | lb | ub | gap | tempo_s | status")

            res_mtz = resolver_tsp_mtz(problema)
            print_result(problema, "MTZ", res_mtz)

            res_mcf = resolver_tsp_mcf(problema)
            print_result(problema, "MCF", res_mcf)
        except Exception as erro:
            print(f"Erro ao executar {arquivo_tsp.name}: {erro}")


if __name__ == "__main__":
    main()