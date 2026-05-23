"""Grados de libertad e identificación: momentos S vs parámetros libres."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from semopy import Model
from semopy.stats import calc_dof


# Si GL / momentos supera este ratio, hay demasiados GL (pocos parámetros → modelo muy rígido).
MAX_GL_RATIO_BALANCED = 0.75


@dataclass(frozen=True)
class IdentificationSummary:
    p: int
    n_varianzas: int
    n_covarianzas: int
    n_momentos: int
    n_parametros_libres: int
    grados_libertad: int
    estado: str
    equilibrio: str
    formula_momentos: str


def covariance_moments_count(p: int) -> tuple[int, int, int]:
    """
    Elementos únicos de la matriz de covarianzas observada S (p×p simétrica).

    - p varianzas en la diagonal
    - p(p-1)/2 covarianzas fuera de diagonal
    - Total momentos = p(p+1)/2
      (p=2 → 2×(2+1)/2 = 2×3/2 = 3: var₁, var₂, cov₁₂;
       p=5 → 5×6/2 = 15)
    """
    if p < 1:
        return 0, 0, 0
    n_var = p
    n_cov = p * (p - 1) // 2
    n_mom = p * (p + 1) // 2
    return n_var, n_cov, n_mom


def summarize_identification(model: Model) -> IdentificationSummary:
    p = len(model.vars["observed"])
    n_var, n_cov, n_mom = covariance_moments_count(p)
    t = len(model.param_vals)
    gl = int(calc_dof(model))
    estado, equilibrio = _classify(gl, n_mom)
    formula = f"{p}×{p + 1}/2 = {n_mom}"
    return IdentificationSummary(
        p=p,
        n_varianzas=n_var,
        n_covarianzas=n_cov,
        n_momentos=n_mom,
        n_parametros_libres=t,
        grados_libertad=gl,
        estado=estado,
        equilibrio=equilibrio,
        formula_momentos=formula,
    )


def ejemplo_momentos_2x2() -> pd.DataFrame:
    """
    Caso mínimo 2×2 con notación del diagrama (V1, V2).

    V1 y V2 son variables observadas (ítems), no abreviatura de «varianza».
    """
    n_var, n_cov, n_mom = covariance_moments_count(2)
    return pd.DataFrame(
        [
            {
                "simbolo_diagrama": "V1",
                "que_es": "Variable observada 1 (ítem; en el estudio → CAL1)",
                "celda_en_S": "S(V1,V1)",
                "tipo_dato": "Varianza de V1",
                "cuenta": "1/3",
            },
            {
                "simbolo_diagrama": "V2",
                "que_es": "Variable observada 2 (ítem; en el estudio → CAL2)",
                "celda_en_S": "S(V2,V2)",
                "tipo_dato": "Varianza de V2",
                "cuenta": "2/3",
            },
            {
                "simbolo_diagrama": "V1 y V2",
                "que_es": "Misma covarianza en la fila V1 o en la fila V2 (S simétrica)",
                "celda_en_S": "S(V1,V2) = S(V2,V1)",
                "tipo_dato": "Covarianza entre V1 y V2",
                "cuenta": "3/3",
            },
            {
                "simbolo_diagrama": "—",
                "que_es": "Total de datos únicos en la matriz 2×2",
                "celda_en_S": "p×(p+1)/2",
                "tipo_dato": f"= 2×(2+1)/2 = 2×3/2 = {n_mom} ({n_var} varianzas + {n_cov} cov.)",
                "cuenta": f"{n_mom} datos",
            },
        ]
    )


def identification_report(model: Model) -> pd.DataFrame:
    """Hoja didáctica: DATA (S) vs parámetros vs GL."""
    s = summarize_identification(model)
    p = s.p
    rows = [
        {
            "concepto": "p (variables observadas en S)",
            "valor": p,
            "formula": "ítems en Matriz_Covarianzas",
        },
        {
            "concepto": "Varianzas en S (diagonal)",
            "valor": s.n_varianzas,
            "formula": f"p = {p}",
        },
        {
            "concepto": "Covarianzas únicas en S",
            "valor": s.n_covarianzas,
            "formula": f"p×(p−1)/2 = {p}×{p - 1}/2 = {s.n_covarianzas}",
        },
        {
            "concepto": "Momentos únicos (matriz S completa)",
            "valor": s.n_momentos,
            "formula": s.formula_momentos,
        },
        {
            "concepto": "Parámetros libres estimados (t)",
            "valor": s.n_parametros_libres,
            "formula": "Reglas 1–4 y 6 (semopy)",
        },
        {
            "concepto": "Grados de libertad (GL)",
            "valor": s.grados_libertad,
            "formula": f"p×(p+1)/2 − t = {s.n_momentos} − {s.n_parametros_libres} = {s.grados_libertad}",
        },
        {
            "concepto": "Estado de identificación",
            "valor": s.estado,
            "formula": "GL<0 subidentificado; GL=0 exacto; GL>0 sobreidentificado",
        },
        {
            "concepto": "Equilibrio GL / momentos",
            "valor": s.equilibrio,
            "formula": (
                f"ratio GL/momentos = {s.grados_libertad}/{s.n_momentos}"
                if s.n_momentos
                else "—"
            ),
        },
    ]
    return pd.DataFrame(rows)


def identification_warnings(model: Model) -> list[dict]:
    s = summarize_identification(model)
    rows: list[dict] = []
    gl, m = s.grados_libertad, s.n_momentos

    if gl < 0:
        rows.append(
            {
                "tipo": "identificacion_gl",
                "mensaje": (
                    f"GL={gl} < 0: modelo subidentificado "
                    f"({m} momentos en S, {s.n_parametros_libres} parámetros libres). "
                    f"Reduzca parámetros o añada restricciones (Regla 6)."
                ),
            }
        )
    elif gl == 0:
        rows.append(
            {
                "tipo": "identificacion_gl",
                "mensaje": (
                    f"GL=0: identificación exacta ({m} momentos = {s.n_parametros_libres} parámetros). "
                    "El ajuste puede ser perfecto pero el modelo es frágil."
                ),
            }
        )
    elif m > 0 and gl / m > MAX_GL_RATIO_BALANCED:
        pct = round(100 * gl / m, 1)
        rows.append(
            {
                "tipo": "identificacion_gl",
                "mensaje": (
                    f"GL={gl} es alto respecto a los {m} momentos de S ({pct}% de momentos libres). "
                    "Demasiados grados de libertad: pocos parámetros para explicar las covarianzas; "
                    "revise si el modelo está demasiado restringido."
                ),
            }
        )
    elif gl > 0:
        p = s.p
        rows.append(
            {
                "tipo": "identificacion_gl",
                "mensaje": (
                    f"GL={gl} > 0 (sobreidentificado): {m} momentos − {s.n_parametros_libres} parámetros. "
                    f"Covarianzas en S: {s.n_covarianzas} (= {p}×{p - 1}/2); "
                    f"total simétrico: {s.formula_momentos}."
                ),
            }
        )
    return rows


def _classify(gl: int, n_moments: int) -> tuple[str, str]:
    if gl < 0:
        return "Subidentificado", "No válido (GL negativos)"
    if gl == 0:
        return "Exactamente identificado", "Frágil (GL=0)"
    if n_moments > 0 and gl / n_moments > MAX_GL_RATIO_BALANCED:
        return "Sobreidentificado", "Desequilibrado (demasiados GL)"
    return "Sobreidentificado", "Equilibrado"


def append_fit_identification_rows(fit_df: pd.DataFrame, model: Model) -> pd.DataFrame:
    """Añade filas de momentos y GL a Fit_Indices."""
    s = summarize_identification(model)
    extra = [
        {"indice": "p_observadas", "valor": float(s.p)},
        {"indice": "momentos_S", "valor": float(s.n_momentos)},
        {"indice": "covarianzas_unicas", "valor": float(s.n_covarianzas)},
        {"indice": "parametros_libres", "valor": float(s.n_parametros_libres)},
        {"indice": "DoF_verificacion", "valor": float(s.grados_libertad)},
        {"indice": "ratio_DoF_momentos", "valor": float(s.grados_libertad / s.n_momentos) if s.n_momentos else None},
    ]
    return pd.concat([fit_df, pd.DataFrame(extra)], ignore_index=True)
