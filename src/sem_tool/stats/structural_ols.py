"""Regresión OLS sobre puntuaciones factoriales (formato Excel / diapositiva)."""

from __future__ import annotations

import pandas as pd

from sem_tool.stats.ols_report import OlsRegressionReport, ols_simple_regression


def ols_reports_from_scores(
    scores: pd.DataFrame,
    paths: list[tuple[str, str]],
) -> list[OlsRegressionReport]:
    """
    Una regresión y = a + b*x por cada ruta estructural, usando scores latentes.

    paths: lista de (X, Y) ej. [("Calidad", "Satisfaccion")]
    """
    reports: list[OlsRegressionReport] = []
    for x_name, y_name in paths:
        if x_name not in scores.columns or y_name not in scores.columns:
            continue
        rep = ols_simple_regression(
            scores[y_name],
            scores[x_name],
            name_y=y_name,
            name_x=x_name,
        )
        reports.append(rep)
    return reports


def structural_paths_from_beta(beta: pd.DataFrame) -> list[tuple[str, str]]:
    paths = []
    if beta is None or beta.empty:
        return paths
    for y in beta.index:
        for x in beta.columns:
            val = beta.loc[y, x]
            if val is not None and abs(float(val)) > 1e-8:
                paths.append((str(x), str(y)))
    return paths
