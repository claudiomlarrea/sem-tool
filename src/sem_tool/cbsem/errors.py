"""Errores de medida (E) y estructurales (D) del diagrama SEM."""

from __future__ import annotations

import pandas as pd
from semopy import Model
from semopy.inspector import inspect_matrices


def export_error_tables(model: Model) -> dict[str, pd.DataFrame]:
    """
    E1–En: varianzas de error de medida (Theta, diagonal).
    D: perturbaciones en factores endógenos (Psi, residuales estructurales).
    """
    mats = inspect_matrices(model)
    sheets: dict[str, pd.DataFrame] = {}

    theta = mats.get("Theta")
    if theta is not None and not theta.empty:
        rows = []
        for item in theta.index:
            val = theta.loc[item, item]
            if val is not None and float(val) > 1e-10:
                rows.append(
                    {
                        "error": f"E_{item}",
                        "variable_observada_V": item,
                        "varianza_error": float(val),
                        "tipo": "Error de medida (E → V)",
                    }
                )
        sheets["Errores_Medicion"] = pd.DataFrame(rows) if rows else pd.DataFrame()

    psi = mats.get("Psi")
    beta = mats.get("Beta")
    if psi is not None and not psi.empty and beta is not None:
        endogenous = []
        for y in beta.index:
            if any(
                beta.loc[y, x] and abs(float(beta.loc[y, x])) > 1e-8
                for x in beta.columns
            ):
                endogenous.append(y)
        rows = []
        for lv in endogenous:
            if lv in psi.index:
                rows.append(
                    {
                        "error": f"D_{lv}",
                        "factor_latente_F": lv,
                        "varianza_perturbacion": float(psi.loc[lv, lv]),
                        "tipo": "Error estructural (D → F)",
                        "nota": "Parte de F2 no explicada por F1",
                    }
                )
        if rows:
            sheets["Errores_Estructurales"] = pd.DataFrame(rows)

    return sheets
