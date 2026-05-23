"""Excel sheet and column contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

SHEET_DATOS = "Datos"
SHEET_DATOS_COV = "Datos_cov"  # alias legado; preferir Matriz_Covarianzas
SHEET_DESCRIPTIVOS = "Descriptivos"
SHEET_COVARIANZA = "Matriz_Covarianzas"
SHEET_CORRELACION = "Matriz_Correlaciones"
SHEET_MEDIAS = "Medias"
SHEET_COVARIANZAS_PARES = "Covarianzas_Pares"
SHEET_MODELO_CB = "Modelo_CB"
SHEET_MODELO_PLS = "Modelo_PLS"
SHEET_CONFIG = "Config"
SHEET_HIPOTESIS = "Hipotesis"
SHEET_INDICADORES = "Indicadores"
SHEET_TIPOS_VARIABLES = "Tipos_Variables"

DESCRIPTIVE_SHEETS = (
    SHEET_DESCRIPTIVOS,
    SHEET_COVARIANZA,
    SHEET_COVARIANZAS_PARES,
    SHEET_CORRELACION,
    SHEET_MEDIAS,
    "Info_Descriptivos",
)

CB_RESULT_SHEETS = (
    "Fit_Indices",
    "Paths_Estandarizados",
    "Paths_NoEstandarizados",
    "Loadings",
    "Matriz_Observada_DATA",
    "Matriz_Implicita_MODEL",
    "Matriz_Residual",
    "Residuales_Pares",
    "Resumen_DATA_MODEL_RESIDUAL",
    "Ecuaciones_Structurales",
    "Regresion_Structural",
    "Regresion_Estadisticos",
    "Regresion_ANOVA",
    "Regresion_Coeficientes",
    "Warnings",
)

PLS_RESULT_SHEETS = (
    "Outer_Loadings",
    "Paths",
    "Bootstraps",
    "R2",
    "Regresion_Structural",
    "Regresion_Estadisticos",
    "Regresion_ANOVA",
    "Regresion_Coeficientes",
    "Efectos_f2",
    "AVE_CR",
    "Fornell_Larcker",
    "HTMT",
    "VIF",
    "Warnings",
)

CB_COLUMNS = ("tipo", "lhs", "op", "rhs", "label", "fixed")
PLS_INDICATOR_COLUMNS = ("constructo", "indicador", "modo")
PLS_PATH_COLUMNS = ("ruta_origen", "ruta_destino")


@dataclass(frozen=True)
class WorkbookMode:
    cb: bool = False
    pls: bool = False


def sheets_for_mode(mode: str) -> tuple[str, ...]:
    if mode == "cb":
        return CB_RESULT_SHEETS
    if mode == "pls":
        return PLS_RESULT_SHEETS
    raise ValueError(f"Unknown mode: {mode}")


def validate_columns(df_columns: Sequence[str], required: Sequence[str], sheet: str) -> None:
    missing = [c for c in required if c not in df_columns]
    if missing:
        raise ValueError(
            f"Hoja '{sheet}': faltan columnas {missing}. "
            f"Requeridas: {list(required)}. Encontradas: {list(df_columns)}"
        )
