#!/usr/bin/env python3
"""Genera ejemplos de encuesta restaurante en examples/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.io.excel import create_restaurant_survey_workbook


def main() -> None:
    examples = ROOT / "examples"
    examples.mkdir(exist_ok=True)
    create_restaurant_survey_workbook(
        examples / "encuesta_restaurante_20.xlsx",
        n_respondents=20,
        include_data=True,
        min_observations=15,
    )
    create_restaurant_survey_workbook(
        examples / "plantilla_restaurante_vacia.xlsx",
        n_respondents=0,
        include_data=False,
        min_observations=15,
    )
    print("Creados:")
    print(" - examples/encuesta_restaurante_20.xlsx (20 clientes)")
    print(" - examples/plantilla_restaurante_vacia.xlsx (solo estructura)")


if __name__ == "__main__":
    main()
