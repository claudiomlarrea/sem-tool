"""Referencia del sistema PLS-SEM (SmartPLS) en sem-tool."""

from __future__ import annotations

import pandas as pd


def sistema_smartpls_catalog() -> pd.DataFrame:
    """Flujo SmartPLS ↔ sem-tool (varianza, bootstrap, calidad de medida)."""
    return pd.DataFrame(
        [
            {
                "fase_smartpls": "1. Datos",
                "que_hace": "Importar variables métricas (Likert, etc.)",
                "sem_tool": "Hoja Datos + sem-tool descriptivos",
                "salida_excel": "Descriptivos, Matriz_Covarianzas",
            },
            {
                "fase_smartpls": "2. Modelo",
                "que_hace": "Diagrama: constructos, indicadores, rutas",
                "sem_tool": "Hoja Modelo_PLS (constructo, indicador, modo, rutas)",
                "salida_excel": "Diagrama_SEM, Hipotesis (opcional)",
            },
            {
                "fase_smartpls": "3. Estimación PLS",
                "que_hace": "Algoritmo PLS (varianza explicada, no χ² global)",
                "sem_tool": "sem-tool pls",
                "salida_excel": "Outer_Loadings, Paths",
            },
            {
                "fase_smartpls": "4. Bootstrapping",
                "que_hace": "Significancia de cargas y rutas (p. ej. 5000)",
                "sem_tool": "sem-tool pls --bootstraps 5000 --processes 2",
                "salida_excel": "Bootstraps",
            },
            {
                "fase_smartpls": "5. Calidad de medida",
                "que_hace": "Cargas externas, AVE, CR, discriminant validity",
                "sem_tool": "Métricas automáticas",
                "salida_excel": "AVE_CR, Fornell_Larcker, HTMT, VIF",
            },
            {
                "fase_smartpls": "6. Modelo estructural",
                "que_hace": "Coeficientes de ruta, R², efectos f²",
                "sem_tool": "Paths + regresión sobre scores",
                "salida_excel": "Paths, R2, Efectos_f2, Regresion_Structural, Regresion_*",
            },
        ]
    )


def smartpls_vs_cbsem() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "tema": "Objetivo",
                "CB_SEM_EQS": "Reproducir matriz de covarianzas S (Σ ≈ S)",
                "PLS_SmartPLS": "Maximizar varianza explicada (R² de constructos)",
            },
            {
                "tema": "Ajuste global",
                "CB_SEM_EQS": "χ², CFI, RMSEA (Fit_Indices)",
                "PLS_SmartPLS": "No hay χ²; evalúa cargas, AVE, HTMT, bootstrap",
            },
            {
                "tema": "Muestra",
                "CB_SEM_EQS": "N grande (≥200 recomendado)",
                "PLS_SmartPLS": "Muestras menores toleradas; bootstrap fiable con N≥100",
            },
            {
                "tema": "Comando sem-tool",
                "CB_SEM_EQS": "sem-tool cb",
                "PLS_SmartPLS": "sem-tool pls",
            },
            {
                "tema": "Hoja de modelo",
                "CB_SEM_EQS": "Modelo_CB (MEAS, REG, COV)",
                "PLS_SmartPLS": "Modelo_PLS (constructo, indicador, modo, rutas)",
            },
        ]
    )


def modelo_pls_columnas() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "columna": "constructo",
                "uso": "Nombre del constructo latente (LV)",
                "ejemplo": "Calidad",
            },
            {
                "columna": "indicador",
                "uso": "Ítem observado (vacío en filas solo de ruta)",
                "ejemplo": "CAL1",
            },
            {
                "columna": "modo",
                "uso": "A = reflexivo (indicadores reflejan constructo); B = formativo",
                "ejemplo": "A",
            },
            {
                "columna": "ruta_origen",
                "uso": "Constructo predictor (estructural)",
                "ejemplo": "Calidad",
            },
            {
                "columna": "ruta_destino",
                "uso": "Constructo dependiente",
                "ejemplo": "Satisfaccion",
            },
            {
                "columna": "nota",
                "uso": "Comentario opcional",
                "ejemplo": "ruta H1",
            },
        ]
    )
