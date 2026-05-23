"""Estructura del diagrama SEM (F1, F2, V, E, D) como en la diapositiva."""

from __future__ import annotations

import pandas as pd

SHEET_DIAGRAMA_SEM = "Diagrama_SEM"


def diagrama_sem_template() -> pd.DataFrame:
    """
    Mapeo didáctico: Calidad (F1) → Satisfacción (F2).

    En la diapositiva: 3 ítems de calidad (V1–V3), 2 de satisfacción (V4–V5).
    sem-tool exige ≥3 ítems por constructo para analizar; use SAT3 como tercer ítem.
    """
    rows = [
        {
            "elemento": "F1",
            "tipo": "Factor latente",
            "nombre_modelo": "Calidad",
            "hipotesis": "Calidad del servicio",
        },
        {
            "elemento": "F2",
            "tipo": "Factor latente",
            "nombre_modelo": "Satisfaccion",
            "hipotesis": "Satisfacción con el servicio",
        },
        {
            "elemento": "V1",
            "tipo": "Variable observada (V = ítem, no ‘varianza’)",
            "nombre_modelo": "CAL1",
            "hipotesis": "En Matriz_Covarianzas: Var(V1) en S(V1,V1); Cov(V1,V2) con V2",
        },
        {
            "elemento": "V2",
            "tipo": "Variable observada (V = ítem, no ‘varianza’)",
            "nombre_modelo": "CAL2",
            "hipotesis": "Cov(V1,V2)=Cov(V2,V1) (misma celda, matriz simétrica)",
        },
        {
            "elemento": "V3",
            "tipo": "Variable observada",
            "nombre_modelo": "CAL3",
            "hipotesis": "Indicador de F1",
        },
        {
            "elemento": "V4",
            "tipo": "Variable observada",
            "nombre_modelo": "SAT1",
            "hipotesis": "Indicador de F2 (satisfacción)",
        },
        {
            "elemento": "V5",
            "tipo": "Variable observada",
            "nombre_modelo": "SAT2",
            "hipotesis": "Indicador de F2",
        },
        {
            "elemento": "SAT3",
            "tipo": "Variable observada",
            "nombre_modelo": "SAT3",
            "hipotesis": "Tercer ítem F2 (requerido: mín. 3 por constructo)",
        },
        {
            "elemento": "E1",
            "tipo": "Error de medida",
            "nombre_modelo": "CAL1",
            "hipotesis": "Error al medir V1",
        },
        {
            "elemento": "E2",
            "tipo": "Error de medida",
            "nombre_modelo": "CAL2",
            "hipotesis": "Error al medir V2",
        },
        {
            "elemento": "E3",
            "tipo": "Error de medida",
            "nombre_modelo": "CAL3",
            "hipotesis": "Error al medir V3",
        },
        {
            "elemento": "E4",
            "tipo": "Error de medida",
            "nombre_modelo": "SAT1",
            "hipotesis": "Error al medir V4",
        },
        {
            "elemento": "E5",
            "tipo": "Error de medida",
            "nombre_modelo": "SAT2",
            "hipotesis": "Error al medir V5",
        },
        {
            "elemento": "D2",
            "tipo": "Error estructural (perturbación)",
            "nombre_modelo": "Satisfaccion",
            "hipotesis": "Residual en F2 no explicado por F1 (disturbance)",
        },
        {
            "elemento": "F1→F2",
            "tipo": "Ruta estructural",
            "nombre_modelo": "Calidad → Satisfaccion",
            "hipotesis": "H1: la satisfacción está relacionada con la calidad",
        },
    ]
    return pd.DataFrame(rows)


def data_summary_from_diagram() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "concepto": ["DATA", "Latentes", "Ruta", "Errores medida", "Error estructural"],
            "descripcion": [
                "V1–V3 calidad + V4–V5 (V6/SAT3) satisfacción en hoja Datos",
                "F1 = Calidad, F2 = Satisfaccion",
                "F2 = a + b·F1  (satisfacción relacionada con calidad)",
                "E1–E5 (y E6 si hay SAT3) → hoja Errores_Medicion",
                "D2 → perturbación en F2 (hoja Errores_Estructurales)",
            ],
        }
    )
