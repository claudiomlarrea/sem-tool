"""
Sistema momento–parámetro para 2 ítems (p=2 → 3 datos, 4 incógnitas).

DATA (muestra, ej. N=500):
  - Var(1), Var(2), Cov(1,2)  → tres números de S

TEORÍA (Σ, Var(F)=1):
  (1) Var(1) = λ₁² + θ₁
  (2) Var(2) = λ₂² + θ₂
  (3) Cov(1,2) = λ₁ × λ₂

Incógnitas: λ₁, λ₂, θ₁, θ₂  → 4 parámetros, 3 ecuaciones → subidentificado
sin restricción (p. ej. fijar λ₁ = 1, Regla 6).
"""

from __future__ import annotations

import pandas as pd


def extract_moments_2_items(
    cov: pd.DataFrame,
    item1: str,
    item2: str,
) -> tuple[float, float, float]:
    v1 = float(cov.loc[item1, item1])
    v2 = float(cov.loc[item2, item2])
    c12 = float(cov.loc[item1, item2])
    return v1, v2, c12


def sistema_ecuaciones_2_items(
    var1: float,
    var2: float,
    cov12: float,
    n_casos: int,
    nombre1: str = "V1",
    nombre2: str = "V2",
) -> pd.DataFrame:
    """Tabla: ecuación DATA = teoría; conteo 3 ecuaciones / 4 incógnitas."""
    return pd.DataFrame(
        [
            {
                "ecuacion": 1,
                "momento_DATA": f"Var({nombre1})",
                "valor_DATA": var1,
                "igual_a_teoría": f"λ₁² + θ₁",
                "incognitas": "λ₁, θ₁",
            },
            {
                "ecuacion": 2,
                "momento_DATA": f"Var({nombre2})",
                "valor_DATA": var2,
                "igual_a_teoría": f"λ₂² + θ₂",
                "incognitas": "λ₂, θ₂",
            },
            {
                "ecuacion": 3,
                "momento_DATA": f"Cov({nombre1},{nombre2})",
                "valor_DATA": cov12,
                "igual_a_teoría": "λ₁ × λ₂",
                "incognitas": "λ₁, λ₂",
            },
            {
                "ecuacion": "—",
                "momento_DATA": f"N = {n_casos} casos",
                "valor_DATA": 3,
                "igual_a_teoría": "Tres momentos únicos en S (2×3/2)",
                "incognitas": "Cuatro parámetros libres sin fijar",
            },
        ]
    )


def conteo_identificacion_2_items() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"concepto": "Ecuaciones (momentos)", "cantidad": 3, "detalle": "Var₁, Var₂, Cov₁₂"},
            {"concepto": "Incógnitas", "cantidad": 4, "detalle": "λ₁, λ₂, θ₁, θ₂"},
            {"concepto": "Diferencia", "cantidad": -1, "detalle": "3 − 4 = −1 → falta 1 restricción"},
            {
                "concepto": "Solución habitual",
                "cantidad": 1,
                "detalle": "Fijar λ₁ = 1 (Regla 6) → 3 ecuaciones, 3 incógnitas (λ₂, θ₁, θ₂)",
            },
            {
                "concepto": "Teoría = práctica",
                "cantidad": 0,
                "detalle": "Tras estimar, Σ teórica debe reproducir los 3 números de S (residual ≈ 0)",
            },
        ]
    )


def solucion_cerrada_lambda1_fijo(
    var1: float,
    var2: float,
    cov12: float,
    lambda1_fijo: float = 1.0,
) -> pd.DataFrame:
    """
    Con λ₁ fijado (p. ej. 1): solución algebraica de las 3 ecuaciones.

    θ₁ = Var(1) − λ₁²
    λ₂ = Cov(1,2) / λ₁
    θ₂ = Var(2) − λ₂²
    """
    lam1 = lambda1_fijo
    theta1 = var1 - lam1**2
    lam2 = cov12 / lam1 if abs(lam1) > 1e-12 else float("nan")
    theta2 = var2 - lam2**2 if lam2 == lam2 else float("nan")

    # Verificación teoría = DATA
    check_v1 = lam1**2 + theta1
    check_v2 = lam2**2 + theta2 if lam2 == lam2 else float("nan")
    check_c = lam1 * lam2 if lam2 == lam2 else float("nan")

    return pd.DataFrame(
        [
            {
                "parametro": "λ₁",
                "valor": lam1,
                "restriccion": "Fijado (métrica del factor)",
            },
            {"parametro": "θ₁", "valor": theta1, "restriccion": f"Var(1)−λ₁² = {var1}−{lam1**2:.6f}"},
            {
                "parametro": "λ₂",
                "valor": lam2,
                "restriccion": f"Cov(1,2)/λ₁ = {cov12}/{lam1}",
            },
            {
                "parametro": "θ₂",
                "valor": theta2,
                "restriccion": f"Var(2)−λ₂²",
            },
            {
                "parametro": "Verif. Var(1)",
                "valor": check_v1,
                "restriccion": f"DATA={var1} → {'OK' if abs(check_v1-var1)<1e-6 else 'revisar'}",
            },
            {
                "parametro": "Verif. Var(2)",
                "valor": check_v2,
                "restriccion": f"DATA={var2} → {'OK' if abs(check_v2-var2)<1e-6 else 'revisar'}",
            },
            {
                "parametro": "Verif. Cov(1,2)",
                "valor": check_c,
                "restriccion": f"DATA={cov12} → {'OK' if abs(check_c-cov12)<1e-6 else 'revisar'}",
            },
        ]
    )


def build_two_item_system_report(
    cov: pd.DataFrame,
    item1: str,
    item2: str,
    n_casos: int,
) -> dict[str, pd.DataFrame]:
    v1, v2, c12 = extract_moments_2_items(cov, item1, item2)
    return {
        "Sistema_3_Ecuaciones": sistema_ecuaciones_2_items(
            v1, v2, c12, n_casos, nombre1=item1, nombre2=item2
        ),
        "Identificacion_2_Items": conteo_identificacion_2_items(),
        "Solucion_lambda1_igual_1": solucion_cerrada_lambda1_fijo(v1, v2, c12, 1.0),
    }


def moment_count_one_factor(p: int) -> tuple[int, int, int]:
    """(ecuaciones, incógnitas con Var(F)=1, grados de libertad)."""
    ecuaciones = p * (p + 1) // 2
    incognitas = 2 * p  # p cargas λ + p errores θ; Var(F)=1 fijada
    gl = ecuaciones - incognitas
    return ecuaciones, incognitas, gl


def sistema_ecuaciones_un_factor(
    cov: pd.DataFrame,
    items: list[str],
    n_casos: int,
    factor: str = "F",
) -> pd.DataFrame:
    """
    Diapositiva: un factor F → V1…Vp, Var(Vi)=λᵢ²+θᵢ, Cov(Vi,Vj)=λᵢλⱼ.
    """
    p = len(items)
    rows: list[dict] = []
    n_eq = 0
    for i, vi in enumerate(items):
        n_eq += 1
        lam = f"λ{i + 1}"
        th = f"θ{i + 1}"
        rows.append(
            {
                "ecuacion": n_eq,
                "tipo": "varianza",
                "momento_DATA": f"Var({vi})",
                "valor_DATA": float(cov.loc[vi, vi]),
                "teoria": f"{lam}² + {th} = Var({vi})",
                "parametros": f"{lam}, {th}",
            }
        )
    for i in range(p):
        for j in range(i + 1, p):
            n_eq += 1
            vi, vj = items[i], items[j]
            rows.append(
                {
                    "ecuacion": n_eq,
                    "tipo": "covarianza",
                    "momento_DATA": f"Cov({vi},{vj})",
                    "valor_DATA": float(cov.loc[vi, vj]),
                    "teoria": f"λ{i + 1} × λ{j + 1} = Cov({vi},{vj})",
                    "parametros": f"λ{i + 1}, λ{j + 1}",
                }
            )
    ecu, inc, gl = moment_count_one_factor(p)
    rows.append(
        {
            "ecuacion": "—",
            "tipo": "resumen",
            "momento_DATA": f"N={n_casos}; factor {factor} con Var(F)=1",
            "valor_DATA": ecu,
            "teoria": f"{p}×({p}+1)/2 = {ecu} ecuaciones",
            "parametros": f"{inc} incógnitas (λ₁…λ{p}, θ₁…θ{p}); GL={gl}",
        }
    )
    return pd.DataFrame(rows)


def conteo_identificacion_un_factor(p: int) -> pd.DataFrame:
    ecu, inc, gl = moment_count_one_factor(p)
    if gl < 0:
        estado = "Subidentificado"
        nota = "Infinitas soluciones (PPT Frederic: no útil)"
    elif gl == 0:
        estado = "Just-identificado"
        nota = "Solución única pero no contrastable (GL=0)"
    else:
        estado = "Sobreidentificado"
        nota = "Objetivo SEM: contrastar S vs Σ (PPT Frederic)"
    return pd.DataFrame(
        [
            {
                "concepto": "Ítems (p)",
                "cantidad": p,
                "detalle": f"Matriz S de {p}×{p}",
            },
            {
                "concepto": "Ecuaciones (momentos)",
                "cantidad": ecu,
                "detalle": f"p×(p+1)/2 = {p}×{p + 1}/2 = {ecu}",
            },
            {
                "concepto": "Incógnitas",
                "cantidad": inc,
                "detalle": f"p cargas λ + p errores θ = 2×{p} (Var(F)=1 fijada)",
            },
            {
                "concepto": "Grados de libertad",
                "cantidad": gl,
                "detalle": f"({p})({p + 1})/2 − {inc} = {gl}",
            },
            {"concepto": "Estado", "cantidad": gl, "detalle": estado},
            {"concepto": "Interpretación", "cantidad": gl, "detalle": nota},
        ]
    )


def ecuaciones_var_cov_separadas(
    cov: pd.DataFrame,
    items: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Como la diapositiva: columna varianzas | columna covarianzas."""
    var_rows = []
    cov_rows = []
    for i, vi in enumerate(items):
        var_rows.append(
            {
                "ecuacion": f"λ{i + 1}² + θ{i + 1} = Var({vi})",
                "valor_DATA": float(cov.loc[vi, vi]),
            }
        )
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            vi, vj = items[i], items[j]
            cov_rows.append(
                {
                    "ecuacion": f"λ{i + 1} × λ{j + 1} = Cov({vi},{vj})",
                    "valor_DATA": float(cov.loc[vi, vj]),
                }
            )
    return pd.DataFrame(var_rows), pd.DataFrame(cov_rows)


def build_one_factor_system_report(
    cov: pd.DataFrame,
    items: list[str],
    n_casos: int,
    factor_name: str = "F",
) -> dict[str, pd.DataFrame]:
    p = len(items)
    ecu, inc, gl = moment_count_one_factor(p)
    var_df, cov_df = ecuaciones_var_cov_separadas(cov, items)
    sheets = {
        f"Sistema_{ecu}_Ecuaciones": sistema_ecuaciones_un_factor(
            cov, items, n_casos, factor_name
        ),
        f"Identificacion_{p}_Items_1_Factor": conteo_identificacion_un_factor(p),
        "Ecuaciones_Varianzas": var_df,
        "Ecuaciones_Covarianzas": cov_df,
    }
    if p == 2:
        sheets.update(
            build_two_item_system_report(cov, items[0], items[1], n_casos)
        )
    return sheets


def slide_cfa_4_items_template() -> pd.DataFrame:
    """Referencia diapositiva: F→V1..V4, E1..E4, 10 ecuaciones, 8 incógnitas, GL=2."""
    return pd.DataFrame(
        [
            {"elemento": "F", "tipo": "Factor latente", "fijado": "Var(F)=1"},
            {"elemento": "V1-V4", "tipo": "Variables observadas", "fijado": "Cargas λ₁…λ₄"},
            {"elemento": "E1-E4", "tipo": "Errores de medida", "fijado": "Varianzas θ₁…θ₄"},
            {"elemento": "10 ecuaciones", "tipo": "Momentos en S", "fijado": "4×5/2 = 10"},
            {"elemento": "8 incógnitas", "tipo": "Parámetros libres", "fijado": "λ₁…λ₄ y θ₁…θ₄"},
            {"elemento": "GL=2", "tipo": "Grados de libertad", "fijado": "10−8=2 > 0 → sobreidentificado"},
        ]
    )
