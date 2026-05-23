"""
Matriz Σ (teoría / tesis) vs matriz S (datos).

Notación del dibujo (Var(F)=1 en la parte teórica):
  - Var(ítem 1) = λ₁² + σ₁   (σ = varianza del error de medida)
  - Cov(1,2) = λ₁ × λ₂

Forma general estimada por semopy (ψ = varianza del factor):
  - Var = λ²ψ + θ
  - Cov = λ₁ × λ₂ × ψ
"""

from __future__ import annotations

import pandas as pd
from semopy import Model
from semopy.inspector import inspect_matrices

# Var(F) = 1 en la Σ teórica del dibujo (parte superior = teoría).
PSI_TESIS = 1.0


def build_sigma_tesis_matrix(model: Model) -> pd.DataFrame:
    """
    Σ teórica según el dibujo: misma estructura, Var(F)=1.

    Diagonal: λᵢ² + σᵢ. Fuera de diagonal (mismo factor): λᵢ × λⱼ.
    Entre factores distintos: se toma la celda del modelo estimado (rutas).
    """
    mats = inspect_matrices(model)
    lam = mats.get("Lambda")
    theta = mats.get("Theta")
    if lam is None or lam.empty:
        return pd.DataFrame()

    obs = list(model.vars["observed"])
    full_sigma, _ = model.calc_sigma()
    full = pd.DataFrame(full_sigma, index=obs, columns=obs)
    item_factor = _primary_factor_per_item(lam)

    sigma = pd.DataFrame(0.0, index=obs, columns=obs)
    for vi in obs:
        for vj in obs:
            fi, fj = item_factor.get(vi), item_factor.get(vj)
            li = _loading(lam, vi, fi)
            lj = _loading(lam, vj, fj)
            if vi == vj:
                sig_err = _theta_diag(theta, vi) or 0.0
                sigma.loc[vi, vj] = (li**2 + sig_err) if li is not None else sig_err
            elif fi and fi == fj and li is not None and lj is not None:
                sigma.loc[vi, vj] = li * lj * PSI_TESIS
            else:
                sigma.loc[vi, vj] = float(full.loc[vi, vj])
    return sigma


def sigma_tesis_explicacion() -> pd.DataFrame:
    """Texto fijo: parte superior del dibujo = Σ (teoría)."""
    return pd.DataFrame(
        [
            {
                "parte_dibujo": "Arriba (teoría)",
                "simbolo": "Σ (sigma griega)",
                "que_es": "Matriz de covarianzas que impone TU modelo según parámetros λ y σ",
                "nota": "En Excel: hoja Matriz_Sigma_Teoria",
            },
            {
                "parte_dibujo": "Abajo (datos)",
                "simbolo": "S",
                "que_es": "Matriz observada (DATA) — Matriz_Covarianzas",
                "nota": "DATA = Σ (modelo) + residual",
            },
            {
                "parte_dibujo": "Diagonal ítem 1",
                "simbolo": "Σ(1,1)",
                "que_es": "Varianza del ítem 1 = covarianza de 1 consigo misma",
                "nota": "Fórmula tesis: λ₁² + σ₁",
            },
            {
                "parte_dibujo": "Fuera diagonal 1–2",
                "simbolo": "Σ(1,2)",
                "que_es": "Covarianza entre ítem 1 e ítem 2",
                "nota": "Fórmula tesis: λ₁ × λ₂ (con Var(F)=1)",
            },
        ]
    )


def covariance_hypotheses_table(
    model: Model,
    cov_observed: pd.DataFrame,
    sigma_implicit: pd.DataFrame,
) -> pd.DataFrame:
    """Cada celda de S con fórmula del dibujo (tesis) y fórmula estimada (ψ, θ)."""
    mats = inspect_matrices(model)
    lam = mats.get("Lambda")
    psi = mats.get("Psi")
    theta = mats.get("Theta")
    sigma_tesis = build_sigma_tesis_matrix(model)
    if lam is None or lam.empty:
        return _pedagogy_only()

    obs = list(model.vars["observed"])
    item_factor = _primary_factor_per_item(lam)
    rows: list[dict] = []

    for i, vi in enumerate(obs):
        for j, vj in enumerate(obs):
            if j < i:
                continue
            s_data = float(cov_observed.loc[vi, vj])
            s_model = float(sigma_implicit.loc[vi, vj])
            s_tesis = float(sigma_tesis.loc[vi, vj]) if not sigma_tesis.empty else None
            res = s_data - s_model

            if vi == vj:
                f = item_factor.get(vi)
                lv = _loading(lam, vi, f)
                pv = _psi_diag(psi, f)
                sig_err = _theta_diag(theta, vi)
                tesis_val = (lv**2 + sig_err) if lv is not None and sig_err is not None else None
                est_val = (
                    lv**2 * pv + sig_err
                    if None not in (lv, pv, sig_err)
                    else None
                )
                rows.append(
                    {
                        "variable_1": vi,
                        "variable_2": vj,
                        "tipo": "varianza",
                        "celda_Sigma": f"Σ({vi},{vj})",
                        "formula_tesis": "λ² + σ  (varianza del ítem; línea central del dibujo)",
                        "formula_estimacion": "λ² × ψ + θ",
                        "factor": f or "",
                        "lambda_1": lv,
                        "sigma_error": sig_err,
                        "psi_factor": pv,
                        "valor_Sigma_tesis": s_tesis,
                        "valor_Sigma_modelo": s_model,
                        "producto_tesis": tesis_val,
                        "producto_estimacion": est_val,
                        "valor_DATA": s_data,
                        "residual_DATA_menos_modelo": res,
                    }
                )
                continue

            fi, fj = item_factor.get(vi), item_factor.get(vj)
            li = _loading(lam, vi, fi)
            lj = _loading(lam, vj, fj)

            if fi and fi == fj:
                pv = _psi_diag(psi, fi)
                tesis_val = li * lj if None not in (li, lj) else None
                est_val = li * lj * pv if None not in (li, lj, pv) else None
                formula_t = "λ₁ × λ₂"
                formula_e = "λ₁ × λ₂ × ψ"
                hip = "Covarianza entre ítems del mismo factor (tu hipótesis en Σ)"
            else:
                tesis_val = None
                est_val = None
                formula_t = "—"
                formula_e = "Σ completa (Λ, Ψ, rutas β)"
                hip = "Ítems de factores distintos: ver Matriz_Sigma_Modelo"

            rows.append(
                {
                    "variable_1": vi,
                    "variable_2": vj,
                    "tipo": "covarianza",
                    "celda_Sigma": f"Σ({vi},{vj})",
                    "formula_tesis": formula_t,
                    "formula_estimacion": formula_e,
                    "hipotesis": hip,
                    "factor": f"{fi}={fj}" if fi == fj else f"{fi}↔{fj}",
                    "lambda_1": li,
                    "lambda_2": lj,
                    "sigma_error": None,
                    "psi_factor": _psi_diag(psi, fi) if fi == fj else None,
                    "valor_Sigma_tesis": s_tesis,
                    "valor_Sigma_modelo": s_model,
                    "producto_tesis": tesis_val,
                    "producto_estimacion": est_val,
                    "valor_DATA": s_data,
                    "residual_DATA_menos_modelo": res,
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        df["coincide_tesis_con_modelo"] = df.apply(_matches_tesis_model, axis=1)
        df["coincide_estimacion_con_modelo"] = df.apply(_matches_est_model, axis=1)
    return df


def ejemplo_hipotesis_v1_v2() -> pd.DataFrame:
    """Caso 2×2 del dibujo (V1, V2, mismo factor; Σ arriba, S abajo)."""
    return pd.DataFrame(
        [
            {
                "celda_Sigma": "Σ(V1,V2)",
                "formula_tesis": "λ₁ × λ₂",
                "significado": "Covarianza entre 1 y 2 según tu estructura",
                "matriz": "Parte superior del dibujo (teoría)",
            },
            {
                "celda_Sigma": "Σ(V1,V1)",
                "formula_tesis": "λ₁² + σ₁",
                "significado": "Varianza del ítem 1 (fila/columna central de V1)",
                "matriz": "Cov(V1,V1) = Var(V1)",
            },
            {
                "celda_Sigma": "Σ(V2,V2)",
                "formula_tesis": "λ₂² + σ₂",
                "significado": "Varianza del ítem 2 (segunda línea/diagonal)",
                "matriz": "Cov(V2,V2) = Var(V2)",
            },
            {
                "celda_Sigma": "—",
                "formula_tesis": "Var(F) = 1 en la Σ teórica",
                "significado": "Por eso Cov = λ₁λ₂ sin ψ; en estimación ψ puede ≠ 1 → λ₁λ₂ψ",
                "matriz": "Matriz_Sigma_Teoria vs Matriz_Implicita_MODEL",
            },
        ]
    )


def _pedagogy_only() -> pd.DataFrame:
    return ejemplo_hipotesis_v1_v2()


def _primary_factor_per_item(lam: pd.DataFrame) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in lam.index:
        col = lam.loc[item]
        hits = col[col.abs() > 1e-8] if hasattr(col, "abs") else col
        if len(hits) == 0:
            continue
        best = hits.abs().idxmax() if hasattr(hits, "abs") else hits.index[0]
        out[str(item)] = str(best)
    return out


def _loading(lam: pd.DataFrame, item: str, factor: str | None) -> float | None:
    if not factor or factor not in lam.columns or item not in lam.index:
        return None
    v = float(lam.loc[item, factor])
    return v if abs(v) > 1e-12 else None


def _psi_diag(psi: pd.DataFrame | None, factor: str | None) -> float | None:
    if psi is None or not factor or factor not in psi.index:
        return None
    return float(psi.loc[factor, factor])


def _theta_diag(theta: pd.DataFrame | None, item: str) -> float | None:
    if theta is None or item not in theta.index:
        return None
    return float(theta.loc[item, item])


def _matches_tesis_model(row: pd.Series) -> str:
    a, b = row.get("valor_Sigma_tesis"), row.get("valor_Sigma_modelo")
    return _yes_no_close(a, b, tol=0.05)


def _matches_est_model(row: pd.Series) -> str:
    a, b = row.get("producto_estimacion"), row.get("valor_Sigma_modelo")
    return _yes_no_close(a, b, tol=1e-4)


def _yes_no_close(a, b, tol: float) -> str:
    if a is None or b is None:
        return "—"
    try:
        return "Sí" if abs(float(a) - float(b)) < tol else "No"
    except (TypeError, ValueError):
        return "—"
