#!/usr/bin/env python3
"""Generate example workbooks: Calidad (F1) → Satisfacción (F2).

NO usar como entrada de Streamlit Cloud — solo CLI:
    python scripts/build_examples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.cbsem.fit import export_cbsem, run_cbsem
from sem_tool.io.excel import create_template
from sem_tool.plsem.estimate import export_plsem, run_plsem


def _likert_data(
    rng: np.random.Generator,
    n: int,
    latent: np.ndarray,
    prefix: str,
    n_items: int = 4,
    n_categories: int = 5,
) -> dict[str, np.ndarray]:
    """Simula respuestas ordinales (1..k) a partir de un factor latente."""
    cols = {}
    for i in range(1, n_items + 1):
        noise = rng.normal(scale=0.8, size=n)
        continuous = latent + noise
        # percentiles → categorías Likert
        ranks = pd.Series(continuous).rank(method="average").values
        cats = np.ceil(ranks / (n / n_categories)).astype(int)
        cats = np.clip(cats, 1, n_categories)
        cols[f"{prefix}{i}"] = cats
    return cols


def _hipotesis_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "origen": "Calidad",
                "destino": "Satisfaccion",
                "hipotesis": "H1: La calidad percibida impacta positivamente la satisfacción",
                "referencia": "Parasuraman et al. (1988); adaptar a su contexto",
                "argumento": "La literatura en servicios vincula calidad con satisfacción post-consumo",
            }
        ]
    )


def _indicadores_df() -> pd.DataFrame:
    rows = []
    for construct, prefix, ref in [
        ("Calidad", "CAL", "SERVQUAL / instrumento de calidad validado"),
        ("Satisfaccion", "SAT", "Escala de satisfacción validada en literatura"),
    ]:
        for n in range(1, 4):
            rows.append(
                {
                    "constructo": construct,
                    "indicador": f"{prefix}{n}",
                    "escala": "Likert",
                    "puntos": 5,
                    "referencia": ref,
                    "notas": "Variable ordinal; mínimo 3 ítems por constructo",
                }
            )
    return pd.DataFrame(rows)


def build_cb_example(path: Path) -> None:
    rng = np.random.default_rng(42)
    n = 200
    calidad = rng.normal(size=n)
    satisfaccion = 0.55 * calidad + rng.normal(scale=0.6, size=n)
    datos = pd.DataFrame(_likert_data(rng, n, calidad, "CAL"))
    datos = datos.join(pd.DataFrame(_likert_data(rng, n, satisfaccion, "SAT")))

    modelo = pd.DataFrame(
        [
            ["medicion", "Calidad", "MEAS", "CAL1 + CAL2 + CAL3", "", "1"],
            ["medicion", "Calidad", "MEAS", "CAL4", "", ""],
            ["medicion", "Satisfaccion", "MEAS", "SAT1 + SAT2 + SAT3", "", "1"],
            ["medicion", "Satisfaccion", "MEAS", "SAT4", "", ""],
            ["estructural", "Satisfaccion", "REG", "Calidad", "", ""],
        ],
        columns=["tipo", "lhs", "op", "rhs", "label", "fixed"],
    )

    create_template(path, "cb")
    with pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
        datos.to_excel(w, sheet_name="Datos", index=False)
        modelo.to_excel(w, sheet_name="Modelo_CB", index=False)
        _hipotesis_df().to_excel(w, sheet_name="Hipotesis", index=False)
        _indicadores_df().to_excel(w, sheet_name="Indicadores", index=False)
        pd.DataFrame({"clave": ["bootstraps"], "valor": [200]}).to_excel(
            w, sheet_name="Config", index=False
        )

    result = run_cbsem(path)
    export_cbsem(path, result)


def build_pls_example(path: Path) -> None:
    rng = np.random.default_rng(7)
    n = 250
    calidad = rng.normal(size=n)
    satisfaccion = 0.5 * calidad + rng.normal(scale=0.55, size=n)
    datos = pd.DataFrame(_likert_data(rng, n, calidad, "CAL"))
    datos = datos.join(pd.DataFrame(_likert_data(rng, n, satisfaccion, "SAT")))

    rows = []
    for construct, prefix in [("Calidad", "CAL"), ("Satisfaccion", "SAT")]:
        for j in range(1, 4):
            rows.append([construct, f"{prefix}{j}", "A", "", "", "ítem reflexivo"])
    rows.append(["Calidad", "", "A", "Calidad", "Satisfaccion", "H1 estructural"])
    modelo = pd.DataFrame(
        rows,
        columns=[
            "constructo",
            "indicador",
            "modo",
            "ruta_origen",
            "ruta_destino",
            "notas",
        ],
    )

    create_template(path, "pls")
    with pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
        datos.to_excel(w, sheet_name="Datos", index=False)
        modelo.to_excel(w, sheet_name="Modelo_PLS", index=False)
        _hipotesis_df().to_excel(w, sheet_name="Hipotesis", index=False)
        _indicadores_df().to_excel(w, sheet_name="Indicadores", index=False)
        pd.DataFrame(
            {"clave": ["bootstraps", "procesos_bootstrap"], "valor": [200, 2]}
        ).to_excel(w, sheet_name="Config", index=False)

    result = run_plsem(path, bootstraps=200, processes=2)
    export_plsem(path, result)


def main() -> None:
    examples = ROOT / "examples"
    templates = ROOT / "templates"
    examples.mkdir(exist_ok=True)
    templates.mkdir(exist_ok=True)

    create_template(templates / "plantilla_cbsem.xlsx", "cb")
    create_template(templates / "plantilla_plsem.xlsx", "pls")
    create_template(templates / "plantilla_completa.xlsx", "both")

    build_cb_example(examples / "ejemplo_cb_academico.xlsx")
    build_pls_example(examples / "ejemplo_pls_negocio.xlsx")

    combined = examples / "estudio_calidad_satisfaccion.xlsx"
    build_pls_example(combined)
    cb_path = examples / "_cb_tmp.xlsx"
    build_cb_example(cb_path)
    for sheet in ("Modelo_CB", "Hipotesis", "Indicadores"):
        df = pd.read_excel(cb_path, sheet_name=sheet)
        with pd.ExcelWriter(
            combined, engine="openpyxl", mode="a", if_sheet_exists="replace"
        ) as w:
            df.to_excel(w, sheet_name=sheet, index=False)
    cb_path.unlink(missing_ok=True)
    print("Ejemplos (Calidad → Satisfacción) en", examples)


if __name__ == "__main__":
    main()
