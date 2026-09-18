from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modelos.mtz_model import carregar_instancia, resolver_tsp_mtz


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    arquivo_tsp = base / "dados" / "berlin52.tsp"

    problema = carregar_instancia(arquivo_tsp)
    res = resolver_tsp_mtz(problema)

    print("instancia | cidade n | Formulação | solver | lb | ub | gap | tempo_s | status")
    print(
        f"{problema.name} | {problema.dimension} | MTZ | HiGHS | "
        f"{res['lb']:.2f} | {res['ub']:.2f} | {res['gap']:.6f} | "
        f"{res['tempo']:.4f} | {res['status']} ({res['message']})"
    )


if __name__ == "__main__":
    main()