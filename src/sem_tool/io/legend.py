"""Leyenda de tipos de variables (diagrama SEM de la diapositiva)."""

from __future__ import annotations

import pandas as pd

SHEET_TIPOS_VARIABLES = "Tipos_Variables"


def tipos_variables_dataframe() -> pd.DataFrame:
    """
    Símbolos del diagrama: V, F, E, D y covarianza entre factores.

    Relación con sem-tool:
    - V → ítems en hoja Datos (CAL1, SAT1, …)
    - F → constructos en Modelo_CB / Modelo_PLS (Calidad, Satisfaccion)
    - E → error de medida (no observado; implícito en CFA)
    - D → perturbación / residual del factor endógeno (Matriz_Residual, Psi)
    """
    return pd.DataFrame(
        [
            {
                "simbolo": "V",
                "forma": "Rectángulo",
                "tipo": "Variable observada",
                "en_sem_tool": "Columnas en hoja Datos",
                "ejemplo": "CAL1, SAT2",
            },
            {
                "simbolo": "F",
                "forma": "Círculo / elipse",
                "tipo": "Variable latente (factor)",
                "en_sem_tool": "Constructo en Modelo_CB o Modelo_PLS",
                "ejemplo": "Calidad, Satisfaccion",
            },
            {
                "simbolo": "E",
                "forma": "Rectángulo E → V",
                "tipo": "Error de medida",
                "en_sem_tool": "Parte no explicada ítem–factor (Theta en CB-SEM)",
                "ejemplo": "Error al medir CAL1",
            },
            {
                "simbolo": "D",
                "forma": "Círculo D → F",
                "tipo": "Error residual (perturbación)",
                "en_sem_tool": "Residual del factor endógeno (disturbance)",
                "ejemplo": "Parte de Satisfaccion no explicada por Calidad",
            },
            {
                "simbolo": "F1↔F2",
                "forma": "Flecha doble curva",
                "tipo": "Covarianza entre factores",
                "en_sem_tool": "Fila tipo COV en Modelo_CB (opcional)",
                "ejemplo": "Calidad ~~ Satisfaccion",
            },
            {
                "simbolo": "→",
                "forma": "Flecha simple",
                "tipo": "Ruta estructural (regresión)",
                "en_sem_tool": "REG: Y ~ X o ruta PLS origen→destino",
                "ejemplo": "Satisfaccion = a + b·Calidad",
            },
        ]
    )
