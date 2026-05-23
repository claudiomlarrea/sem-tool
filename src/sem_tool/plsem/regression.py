"""Regresión PLS: pendiente de rutas y R² por constructo endógeno."""

from __future__ import annotations

import pandas as pd
from plspm.plspm import Plspm


def pls_regression_table(pls: Plspm, inner_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Análisis de regresión PLS: coeficiente de ruta (pendiente) y R².

    En PLS la ruta X→Y es el equivalente a la pendiente en Y = f(X).
    """
    paths = pls.path_coefficients()
    rows: list[dict] = []

    r2_map = _r2_by_construct(inner_summary)

    for dest in paths.index:
        for orig in paths.columns:
            b = paths.loc[dest, orig]
            if b is None or float(b) == 0:
                continue
            b = float(b)
            r2 = r2_map.get(dest)
            rows.append(
                {
                    "variable_dependiente_Y": dest,
                    "variable_independiente_X": orig,
                    "pendiente_b": b,
                    "R2": r2,
                    "R2_pct": round(r2 * 100, 2) if r2 is not None and r2 == r2 else None,
                    "ecuacion": f"{dest} = ({b:.4f})*{orig}",
                    "coeficiente_interes": "pendiente_b",
                    "interpretacion_pendiente": (
                        f"Al aumentar {orig}, {'aumenta' if b > 0 else 'disminuye'} {dest}."
                    ),
                    "nota": "R² del constructo endógeno; significancia en hoja Bootstraps",
                }
            )

    if not rows:
        return pd.DataFrame({"mensaje": ["Sin rutas estructurales en Modelo_PLS."]})
    return pd.DataFrame(rows)


def _r2_by_construct(inner_summary: pd.DataFrame) -> dict[str, float]:
    out: dict[str, float] = {}
    if inner_summary is None or inner_summary.empty:
        return out
    r2_col = None
    for c in inner_summary.columns:
        if "r_squared" in str(c).lower() or str(c).lower() in ("r2", "r²"):
            r2_col = c
            break
    if r2_col is None and len(inner_summary.columns) >= 2:
        r2_col = inner_summary.columns[1]
    for lv in inner_summary.index:
        try:
            out[str(lv)] = float(inner_summary.loc[lv, r2_col])
        except (KeyError, TypeError, ValueError):
            pass
    return out
