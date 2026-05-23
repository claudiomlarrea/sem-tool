"""Análisis de regresión estructural: R² y pendiente (coeficiente clave)."""

from __future__ import annotations

import pandas as pd
from semopy import Model
from semopy.inspector import inspect_list, inspect_matrices


def structural_regression_table(model: Model) -> pd.DataFrame:
    """
    Regresión entre factores latentes: Y = a + b*X.

    Destaca la **pendiente b** (efecto de X sobre Y) y el **R²**
    (varianza de Y explicada por X).
    """
    mats = inspect_matrices(model)
    beta = mats.get("Beta")
    psi = mats.get("Psi")
    if beta is None or psi is None:
        return pd.DataFrame(
            {"mensaje": ["No hay rutas estructurales estimadas en el modelo."]}
        )

    try:
        params = inspect_list(model, information=None, std_est=True)
    except Exception:
        params = pd.DataFrame()

    rows: list[dict] = []

    for y in beta.index:
        predictors = []
        for x in beta.columns:
            b_raw = beta.loc[y, x]
            if b_raw is None or abs(float(b_raw)) < 1e-8:
                continue
            predictors.append(x)
            b = float(b_raw)
            a = 0.0
            r2 = _r2_latent_regression(b, x, y, psi)
            std_b, se_b, z_val, p_val = _lookup_path_stats(params, y, x, b)
            rows.append(
                {
                    "variable_dependiente_Y": y,
                    "variable_independiente_X": x,
                    "intercepto_a": a,
                    "pendiente_b": b,
                    "pendiente_estandarizada": std_b,
                    "error_estandar_b": se_b,
                    "z_valor": z_val,
                    "p_valor": p_val,
                    "R2": r2,
                    "R2_pct": round(r2 * 100, 2) if r2 == r2 else None,
                    "ecuacion": f"{y} = {a:.4f} + ({b:.4f})*{x}",
                    "coeficiente_interes": "pendiente_b",
                    "interpretacion_pendiente": _slope_interpretation(b, x, y),
                }
            )

        if len(predictors) > 1:
            r2_total = _r2_multiple(y, predictors, beta, psi)
            rows.append(
                {
                    "variable_dependiente_Y": y,
                    "variable_independiente_X": " + ".join(predictors),
                    "intercepto_a": 0.0,
                    "pendiente_b": None,
                    "pendiente_estandarizada": None,
                    "error_estandar_b": None,
                    "z_valor": None,
                    "p_valor": None,
                    "R2": r2_total,
                    "R2_pct": round(r2_total * 100, 2) if r2_total == r2_total else None,
                    "ecuacion": f"{y} ~ {' + '.join(predictors)}",
                    "coeficiente_interes": "R2 conjunto",
                    "interpretacion_pendiente": "Varianza total explicada por todos los predictores",
                }
            )

    if not rows:
        return pd.DataFrame(
            {"mensaje": ["Defina rutas REG en Modelo_CB (ej. Satisfaccion ~ Calidad)."]}
        )
    return pd.DataFrame(rows)


def _r2_latent_regression(
    b: float,
    x: str,
    y: str,
    psi: pd.DataFrame,
) -> float:
    """
    R² = Var(b·η_x) / (Var(b·η_x) + Var(ζ_y))
    con Var(ζ_y) = Psi[y,y] y Var(η_x) = Psi[x,x].
    """
    try:
        var_x = float(psi.loc[x, x])
        var_zeta_y = float(psi.loc[y, y])
    except (KeyError, TypeError, ValueError):
        return float("nan")
    if var_x <= 0 or var_zeta_y < 0:
        return float("nan")
    var_explained = (b**2) * var_x
    total = var_explained + var_zeta_y
    if total <= 0:
        return float("nan")
    return float(var_explained / total)


def _r2_multiple(
    y: str,
    predictors: list[str],
    beta: pd.DataFrame,
    psi: pd.DataFrame,
) -> float:
    try:
        var_zeta_y = float(psi.loc[y, y])
    except (KeyError, TypeError, ValueError):
        return float("nan")
    explained = 0.0
    for x in predictors:
        b = float(beta.loc[y, x])
        try:
            var_x = float(psi.loc[x, x])
        except (KeyError, TypeError, ValueError):
            continue
        explained += (b**2) * var_x
    total = explained + var_zeta_y
    if total <= 0:
        return float("nan")
    return float(explained / total)


def _lookup_path_stats(
    params: pd.DataFrame,
    y: str,
    x: str,
    b_default: float,
) -> tuple[float | None, float | None, float | None, float | None]:
    if params is None or params.empty or "op" not in params.columns:
        return None, None, None, None
    mask = (
        (params["op"] == "~")
        & (params["lval"].astype(str) == y)
        & (params["rval"].astype(str) == x)
    )
    hit = params.loc[mask]
    if hit.empty:
        return None, None, None, None
    row = hit.iloc[0]
    std_b = _safe_float(row.get("Est. Std"))
    se_b = _safe_float(row.get("Std. Err"))
    z_val = _safe_float(row.get("z-value"))
    p_val = _safe_float(row.get("p-value"))
    return std_b, se_b, z_val, p_val


def _safe_float(val) -> float | None:
    if val is None or (isinstance(val, float) and val != val):
        return None
    if val == "-" or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _slope_interpretation(b: float, x: str, y: str) -> str:
    if b > 0:
        return f"Al aumentar {x}, aumenta {y} (pendiente positiva)."
    if b < 0:
        return f"Al aumentar {x}, disminuye {y} (pendiente negativa)."
    return f"Sin efecto lineal de {x} sobre {y}."
