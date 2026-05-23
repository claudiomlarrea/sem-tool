"""Media, varianza y covarianzas entre variables (insumo del análisis factorial / SEM)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

from sem_tool.io import excel as xl
from sem_tool.io.schema import (
    SHEET_CORRELACION,
    SHEET_COVARIANZA,
    SHEET_COVARIANZAS_PARES,
    SHEET_DESCRIPTIVOS,
    SHEET_MEDIAS,
)


@dataclass
class DescriptiveResult:
    descriptivos: pd.DataFrame
    covarianza: pd.DataFrame
    correlacion: pd.DataFrame
    covarianzas_pares: pd.DataFrame
    medias: pd.Series
    n_casos: int
    variables: list[str]


def covariance_between(x: pd.Series, y: pd.Series, ddof: int = 1) -> float:
    """Covarianza muestral entre dos variables observadas."""
    pair = pd.concat([x, y], axis=1).dropna()
    if len(pair) < 2:
        return float("nan")
    return float(pair.iloc[:, 0].cov(pair.iloc[:, 1], ddof=ddof))


def pairwise_covariances_table(
    data: pd.DataFrame,
    columns: list[str],
    correlacion: pd.DataFrame,
    ddof: int = 1,
) -> pd.DataFrame:
    """
    Tabla explícita: covarianza entre cada par de variables.

    Es el insumo que resume la relación lineal entre ítems antes del
    análisis factorial / CFA (matriz S en CB-SEM).
    """
    rows: list[dict] = []
    for i, var_x in enumerate(columns):
        for j, var_y in enumerate(columns):
            if j < i:
                continue
            cov_xy = covariance_between(data[var_x], data[var_y], ddof=ddof)
            if var_x == var_y:
                tipo = "varianza"
                corr = 1.0
            else:
                tipo = "covarianza"
                corr = (
                    float(correlacion.loc[var_x, var_y])
                    if var_x in correlacion.index and var_y in correlacion.columns
                    else float("nan")
                )
            rows.append(
                {
                    "variable_1": var_x,
                    "variable_2": var_y,
                    "tipo": tipo,
                    "covarianza": cov_xy,
                    "correlacion": corr,
                }
            )
    return pd.DataFrame(rows)


def compute_descriptives(
    data: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
    pairwise: bool = False,
    min_obs_per_variable: int = 100,
) -> DescriptiveResult:
    """
    Calcula media, varianza y matriz de covarianzas entre todas las variables.

    La matriz de covarianzas S es lo que usa el análisis factorial confirmatorio
    y el CB-SEM (EQS): el modelo reproduce esas covarianzas entre ítems.
    """
    if columns is not None:
        cols = [c for c in columns if c in data.columns]
    else:
        cols = list(data.select_dtypes(include=[np.number]).columns)
    if not cols:
        raise ValueError("No hay variables numéricas para calcular descriptivos.")

    numeric = data[cols].apply(pd.to_numeric, errors="coerce")
    if pairwise:
        clean = numeric
    else:
        clean = numeric.dropna(how="any")
    if clean.empty:
        raise ValueError("No hay filas completas sin datos faltantes.")

    n_listwise = int(clean.shape[0])
    means = clean.mean()
    variances = clean.var(ddof=1)
    stds = clean.std(ddof=1)
    n_por_variable = {c: int(data[c].dropna().shape[0]) for c in cols}

    descriptivos = pd.DataFrame(
        {
            "variable": means.index,
            "observaciones": [n_por_variable.get(v, n_listwise) for v in means.index],
            "observaciones_listwise": n_listwise,
            "cumple_muestra_minima": [
                n_por_variable.get(v, 0) >= min_obs_per_variable for v in means.index
            ],
            "media": means.values,
            "varianza": variances.values,
            "desviacion": stds.values,
        }
    )

    covarianza = clean.cov()  # S: covarianza entre cada par de variables
    correlacion = clean.corr()
    pares = pairwise_covariances_table(clean, cols, correlacion, ddof=1)

    return DescriptiveResult(
        descriptivos=descriptivos,
        covarianza=covarianza,
        correlacion=correlacion,
        covarianzas_pares=pares,
        medias=means,
        n_casos=n_listwise,
        variables=list(means.index),
    )


def export_descriptives_to_workbook(
    workbook_path: Path,
    result: DescriptiveResult,
    min_obs_per_variable: int = 100,
) -> None:
    """Escribe descriptivos y matrices (incl. covarianzas entre pares)."""
    meta = pd.DataFrame(
        {
            "concepto": [
                "n_casos_listwise",
                "n_variables",
                "observaciones_minimas_por_variable",
                "uso",
            ],
            "valor": [
                result.n_casos,
                len(result.variables),
                min_obs_per_variable,
                f"Cada variable debe tener ≥{min_obs_per_variable} respuestas; covarianzas con casos completos",
            ],
        }
    )
    medias_df = result.medias.to_frame(name="media")
    medias_df.index.name = "variable"

    sheets = {
        SHEET_DESCRIPTIVOS: result.descriptivos,
        SHEET_COVARIANZA: result.covarianza,
        SHEET_COVARIANZAS_PARES: result.covarianzas_pares,
        SHEET_CORRELACION: result.correlacion,
        SHEET_MEDIAS: medias_df,
        "Info_Descriptivos": meta,
    }
    xl.write_result_sheets(workbook_path, sheets)


def run_descriptives_for_workbook(
    workbook_path: Path,
    columns: Optional[Iterable[str]] = None,
) -> DescriptiveResult:
    """Lee Datos, calcula covarianzas entre variables y exporta a Excel."""
    from sem_tool.validation.methodology import get_min_observations

    data = xl.read_data(workbook_path)
    min_obs = get_min_observations(workbook_path)
    result = compute_descriptives(data, columns=columns, min_obs_per_variable=min_obs)
    export_descriptives_to_workbook(workbook_path, result, min_obs_per_variable=min_obs)
    return result
