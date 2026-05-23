"""DATA = MODEL + RESIDUAL: covarianza observada vs implícita del modelo."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from semopy import Model
from semopy.inspector import inspect_matrices


def _matrix_to_pairs(mat: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    cols = list(mat.columns)
    for i, vx in enumerate(cols):
        for j, vy in enumerate(cols):
            if j < i:
                continue
            val = float(mat.loc[vx, vy])
            rows.append(
                {
                    "variable_1": vx,
                    "variable_2": vy,
                    "tipo": "varianza" if vx == vy else label,
                    "valor": val,
                }
            )
    return pd.DataFrame(rows)



@dataclass
class CovarianceDecomposition:
    observada: pd.DataFrame
    implicita: pd.DataFrame
    residual: pd.DataFrame
    residuales_pares: pd.DataFrame
    resumen: pd.DataFrame
    ecuaciones: pd.DataFrame
    regresion_structural: pd.DataFrame
    hipotesis_covarianzas: pd.DataFrame
    sigma_tesis: pd.DataFrame
    sigma_tesis_nota: pd.DataFrame


def decompose_covariance(
    model: Model,
    cov_observed: pd.DataFrame,
) -> CovarianceDecomposition:
    """
    Descompone la matriz de covarianzas de los datos (S) en parte explicada
    por el modelo (Sigma) y residual (S - Sigma).
    """
    obs_names = list(model.vars["observed"])
    S = cov_observed.loc[obs_names, obs_names].astype(float)

    sigma_np, _ = model.calc_sigma()
    sigma = pd.DataFrame(sigma_np, index=obs_names, columns=obs_names)
    residual = S - sigma

    residuales_pares = _matrix_to_pairs(residual, "residual")

    resumen = _build_summary(model, S, sigma, residual)
    ecuaciones = _structural_equations(model)
    from sem_tool.cbsem.regression import structural_regression_table

    regresion = structural_regression_table(model)

    from sem_tool.cbsem.covariance_hypotheses import (
        build_sigma_tesis_matrix,
        covariance_hypotheses_table,
        sigma_tesis_explicacion,
    )

    hipotesis = covariance_hypotheses_table(model, S, sigma)
    sigma_tesis = build_sigma_tesis_matrix(model)
    sigma_nota = sigma_tesis_explicacion()

    return CovarianceDecomposition(
        observada=S,
        implicita=sigma,
        residual=residual,
        residuales_pares=residuales_pares,
        resumen=resumen,
        ecuaciones=ecuaciones,
        regresion_structural=regresion,
        hipotesis_covarianzas=hipotesis,
        sigma_tesis=sigma_tesis,
        sigma_tesis_nota=sigma_nota,
    )


def _build_summary(
    model: Model,
    S: pd.DataFrame,
    sigma: pd.DataFrame,
    residual: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        {
            "concepto": "Ecuación fundamental",
            "descripcion": "DATA (S) = MODEL (Sigma implícita) + RESIDUAL (S - Sigma)",
        },
        {
            "concepto": "DATA",
            "descripcion": "Matriz_Covarianzas: covarianzas observadas entre ítems",
        },
        {
            "concepto": "MODEL (Σ estimada)",
            "descripcion": "Matriz_Implicita_MODEL: Σ con parámetros estimados (λ²ψ+θ, λ₁λ₂ψ)",
        },
        {
            "concepto": "Σ teórica (dibujo)",
            "descripcion": "Matriz_Sigma_Teoria: λ²+σ y λ₁λ₂ con Var(F)=1 (tu tesis)",
        },
        {
            "concepto": "RESIDUAL",
            "descripcion": "Matriz_Residual: diferencia no explicada (idealmente cercana a 0)",
        },
    ]
    try:
        from semopy.stats import calc_chi2, calc_dof

        dof = calc_dof(model)
        chi2, pval = calc_chi2(model, dof)
        rows.append(
            {
                "concepto": "Chi-cuadrado de ajuste",
                "descripcion": f"chi2={float(chi2):.4f}, p={float(pval):.4f} (contraste S vs Sigma)",
            }
        )
    except Exception:
        pass

    frob = float(np.linalg.norm(residual.values, ord="fro"))
    rows.append(
        {
            "concepto": "Norma residual (Frobenius)",
            "descripcion": f"{frob:.6f} (menor = mejor ajuste de covarianzas)",
        }
    )
    return pd.DataFrame(rows)


def _structural_equations(model: Model) -> pd.DataFrame:
    """
    Ecuaciones estructurales en forma Y = a + b*X (factores latentes).

    En SEM con medias de factores fijadas en 0: Y = b*X + zeta.
    """
    rows: list[dict] = []
    mats = inspect_matrices(model)
    beta = mats.get("Beta")
    if beta is not None and not beta.empty:
        for y in beta.index:
            for x in beta.columns:
                b = beta.loc[y, x]
                if b is None or (isinstance(b, float) and abs(b) < 1e-8):
                    continue
                b = float(b)
                intercept = 0.0
                rows.append(
                    {
                        "variable_dependiente": y,
                        "variable_independiente": x,
                        "intercepto_a": intercept,
                        "pendiente_b": b,
                        "ecuacion": f"{y} = {intercept:.4f} + ({b:.4f})*{x}",
                        "forma": "Y = a + b*X",
                        "nota": "Medias de factores latentes usualmente fijadas en 0 (a=0)",
                    }
                )

    lam = mats.get("Lambda")
    if lam is not None and not lam.empty:
        for item in lam.index:
            for factor in lam.columns:
                loading = lam.loc[item, factor]
                if loading is None or abs(float(loading)) < 1e-8:
                    continue
                loading = float(loading)
                rows.append(
                    {
                        "variable_dependiente": item,
                        "variable_independiente": factor,
                        "intercepto_a": 0.0,
                        "pendiente_b": loading,
                        "ecuacion": f"{item} = {loading:.4f}*{factor}",
                        "forma": "ítem = lambda*factor",
                        "nota": "Ecuación de medida (análisis factorial)",
                    }
                )

    if not rows:
        rows.append(
            {
                "variable_dependiente": "",
                "ecuacion": "Sin ecuaciones estructurales estimadas",
                "forma": "",
                "nota": "",
            }
        )
    return pd.DataFrame(rows)
