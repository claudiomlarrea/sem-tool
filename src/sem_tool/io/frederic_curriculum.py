"""
Contenido del taller SEM (Frederic Marimon / Marta Mas, UIC).

Fuente: Structural Equation Modeling (SEM).pptx
"""

from __future__ import annotations

import pandas as pd


def indice_taller_frederic() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "slide_aprox": list(range(1, 20)),
            "tema": [
                "Portada: EQS + Smart-PLS CB",
                "Índice del curso",
                "Objetivos: SEM por covarianzas",
                "DATA = MODEL + RESIDUAL",
                "Análisis de varianza",
                "Calidad → Satisfacción (varianza)",
                "Tipos de variables V, F, E, D",
                "Coeficientes estandarizados / no estandarizados",
                "Modelo F1 Calidad → F2 Satisfacción (V1–V5)",
                "Dependientes vs independientes",
                "Ecuaciones de medida y estructural",
                "Reglas parámetros 1–6",
                "Definición del modelo (* libre, 1 fijo)",
                "11 parámetros, GL = 5×6/2 − 11 = 4",
                "Covarianza E1–E3 (−1 gl)",
                "Leyes de covarianzas 1–4",
                "Model fitness: λ²+θ, λᵢλⱼ, matriz Σ vs S",
                "2 ítems: subidentificado (3 ec., 4 inc.)",
                "3 ítems: just-identificado (GL=0)",
            ],
            "hoja_sem_tool": [
                "Curso_Frederic_SEM",
                "Curso_Frederic_SEM",
                "Curso_Frederic_SEM",
                "Resumen_DATA_MODEL_RESIDUAL",
                "Regresion_ANOVA / R2",
                "Regresion_Structural",
                "Tipos_Variables, Diagrama_SEM",
                "Paths_Estandarizados, Paths_NoEstandarizados",
                "Diagrama_SEM, Modelo_CB",
                "Tipos_Variables",
                "Ecuaciones_Structurales",
                "Reglas_Parametros",
                "Modelo_CB, Parametros_Modelo",
                "Identificacion_GL",
                "Modelo_CB (COV)",
                "Leyes_Covarianzas",
                "Hipotesis_Covarianzas, Matriz_Sigma_Teoria",
                "Sistema_3_Ecuaciones",
                "Identificacion_2_Items (GL=0 si p=3)",
            ],
        }
    )


def leyes_covarianzas_frederic() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"ley": 1, "formula": "Cov(X,X) = Var(X)", "uso_en_sem": "Diagonal de S"},
            {
                "ley": 2,
                "formula": "Cov(aX+bY, cZ+dU) = ac·Cov(X,Z)+ad·Cov(X,U)+bc·Cov(Y,Z)+bd·Cov(Y,U)",
                "uso_en_sem": "Desarrollo de Σ implícita",
            },
            {
                "ley": 3,
                "formula": "Var(aX+bY) = a²Var(X)+b²Var(Y)+2ab·Cov(X,Y)",
                "uso_en_sem": "Varianza de ítem = λ²ψ+θ",
            },
            {
                "ley": 4,
                "formula": "Si X⊥Y: Var(aX+bY) = a²Var(X)+b²Var(Y)",
                "uso_en_sem": "F y errores no correlacionados → λ₁λ₂",
            },
        ]
    )


def identificacion_modelo_frederic() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "estado": "Subidentificado",
                "grados_libertad": "< 0",
                "soluciones": "Infinitas",
                "utilidad": "No sirve",
                "ejemplo_ppt": "2 ítems, 4 parámetros, 3 ecuaciones",
            },
            {
                "estado": "Just-identificado",
                "grados_libertad": "= 0",
                "soluciones": "Única",
                "utilidad": "No contrastable (no se puede rechazar)",
                "ejemplo_ppt": "3 ítems, 6 parámetros, 6 ecuaciones",
            },
            {
                "estado": "Sobreidentificado",
                "grados_libertad": "> 0",
                "soluciones": "Contrastable",
                "utilidad": "Objetivo del SEM (comparar S y Σ)",
                "ejemplo_ppt": "4 ítems un factor: GL=2; modelo UIC: GL=4",
            },
        ]
    )


def modelo_uic_calidad_satisfaccion() -> pd.DataFrame:
    """Slides 13–19: F1→V1–V3, F2→V4–V5, F2=β·F1+D2."""
    return pd.DataFrame(
        [
            {"elemento": "F1", "tipo": "Latente exógeno", "ecuacion": "Var(F1) parámetro o fijada=1"},
            {"elemento": "F2", "tipo": "Latente endógeno", "ecuacion": "F2 = β·F1 + D2"},
            {"elemento": "V1–V3", "tipo": "Ítems calidad", "ecuacion": "Vi = αi·F1 + Ei"},
            {"elemento": "V4–V5", "tipo": "Ítems satisfacción", "ecuacion": "Vi = αi·F2 + Ei"},
            {"elemento": "E1–E5", "tipo": "Errores medida", "ecuacion": "Var(Ei) parámetro (regla 1)"},
            {"elemento": "D2", "tipo": "Perturbación", "ecuacion": "Var(D2) parámetro"},
            {
                "elemento": "Conteo PPT",
                "tipo": "p=5 ítems observados",
                "ecuacion": "11 parámetros; GL = 5×6/2 − 11 = 4",
            },
            {
                "elemento": "sem-tool",
                "tipo": "Mínimo 3 ítems/constructo",
                "ecuacion": "Use CAL1–3 + SAT1–3 en Datos; fixed=1 en primer MEAS",
            },
        ]
    )


def logica_ajuste_chi_cuadrado() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "concepto": "Objetivo",
                "detalle": "Minimizar diferencia entre S (datos) y Σ (modelo)",
            },
            {
                "concepto": "T = (n−1)·Fmin",
                "detalle": "T ~ χ² con los mismos gl del modelo",
            },
            {
                "concepto": "H₀",
                "detalle": "No hay diferencia modelo–datos (modelo ajusta)",
            },
            {
                "concepto": "H₁",
                "detalle": "Hay diferencia (modelo no ajusta)",
            },
            {
                "concepto": "Buen ajuste",
                "detalle": "χ² bajo, p > 0.05 (cuidado: N grande infla χ²)",
            },
            {
                "concepto": "Muestra (regla PPT)",
                "detalle": "N ≥ 10×parámetros (regla práctica) o ≥ 5×parámetros (Hu & Bentler)",
            },
            {
                "concepto": "Método estimación",
                "detalle": "ML (semopy/EQS), también GLS y ULS en teoría",
            },
        ]
    )


def equivalencias_eqs_smartpls_output() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "eqs_output": "GOODNESS OF FIT SUMMARY / CHI-SQUARE / PROBABILITY",
                "smartpls_output": "No χ² global (enfoque varianza)",
                "sem_tool": "Fit_Indices + Criterios_Ajuste (CB); Resumen_SmartPLS (PLS)",
            },
            {
                "eqs_output": "MEASUREMENT EQUATIONS (V = λ·F + E, @ significativo)",
                "smartpls_output": "Outer loadings + bootstrap",
                "sem_tool": "Loadings / Outer_Loadings, Bootstraps",
            },
            {
                "eqs_output": "STRUCTURAL EQUATIONS, R²",
                "smartpls_output": "Path coefficients, R²",
                "sem_tool": "Paths, R2, Regresion_Structural",
            },
            {
                "eqs_output": "LAGRANGE MULTIPLIER TEST",
                "smartpls_output": "—",
                "sem_tool": "No implementado (MVP); revise modificaciones en Modelo_CB",
            },
        ]
    )
