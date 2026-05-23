"""Informe de regresión estilo Excel: estadísticos, ANOVA y coeficientes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class OlsRegressionReport:
    """Equivalente a Salida de regresión de Excel (como en diapositiva Análisis de varianza)."""

    estadisticos: pd.DataFrame
    anova: pd.DataFrame
    coeficientes: pd.DataFrame
    variable_y: str
    variable_x: str
    n_obs: int


def ols_simple_regression(
    y: pd.Series,
    x: pd.Series,
    name_y: str = "Y",
    name_x: str = "Variable X 1",
) -> OlsRegressionReport:
    """
    Regresión lineal simple y = a + b*x con tablas ANOVA y coeficientes.

    Replica el formato habitual de Excel / SPSS en español.
    """
    df = pd.concat([y.rename("y"), x.rename("x")], axis=1).dropna()
    min_n = 100
    if len(df) < min_n:
        raise ValueError(
            f"Se necesitan al menos {min_n} observaciones para {name_y} ~ {name_x} "
            f"(n={len(df)})."
        )

    yv = df["y"].values.astype(float)
    xv = df["x"].values.astype(float)
    n = len(yv)
    k = 2  # intercepto + pendiente

    X = np.column_stack([np.ones(n), xv])
    beta, _, _, _ = np.linalg.lstsq(X, yv, rcond=None)
    a, b = float(beta[0]), float(beta[1])
    y_hat = X @ beta
    resid = yv - y_hat

    sse = float(np.sum(resid**2))
    sst = float(np.sum((yv - yv.mean()) ** 2))
    ssr = sst - sse
    if sst <= 0:
        r2 = 0.0
    else:
        r2 = 1.0 - sse / sst

    df_reg = 1
    df_res = n - k
    df_total = n - 1
    msr = ssr / df_reg if df_reg else np.nan
    mse = sse / df_res if df_res > 0 else np.nan
    f_stat = msr / mse if mse and mse > 0 else np.nan
    f_crit_p = float(stats.f.sf(f_stat, df_reg, df_res)) if f_stat == f_stat else np.nan

    r = float(np.corrcoef(xv, yv)[0, 1])
    mult_r = abs(r)
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k) if n > k else r2
    se_reg = float(np.sqrt(mse)) if mse == mse else np.nan

    # Errores estándar de coeficientes
    try:
        var_beta = mse * np.linalg.inv(X.T @ X)
        se_a = float(np.sqrt(var_beta[0, 0]))
        se_b = float(np.sqrt(var_beta[1, 1]))
    except np.linalg.LinAlgError:
        se_a = se_b = np.nan

    t_a = a / se_a if se_a and se_a > 0 else np.nan
    t_b = b / se_b if se_b and se_b > 0 else np.nan
    p_a = float(2 * stats.t.sf(abs(t_a), df_res)) if t_a == t_a else np.nan
    p_b = float(2 * stats.t.sf(abs(t_b), df_res)) if t_b == t_b else np.nan
    t_crit = float(stats.t.ppf(0.975, df_res))
    ic_a = (a - t_crit * se_a, a + t_crit * se_a) if se_a == se_a else (np.nan, np.nan)
    ic_b = (b - t_crit * se_b, b + t_crit * se_b) if se_b == se_b else (np.nan, np.nan)

    estadisticos = pd.DataFrame(
        {
            "Estadística": [
                "Coeficiente de correlación múltiple",
                "Coeficiente de determinación R²",
                "R² ajustado",
                "Error típico",
                "Observaciones",
                "Interpretación R²",
            ],
            "Valor": [
                mult_r,
                r2,
                adj_r2,
                se_reg,
                float(n),
                "Capacidad del modelo para explicar Y; qué tan bien los datos se ajustan",
            ],
        }
    )

    anova = pd.DataFrame(
        {
            "": ["Regresión", "Residuos", "Total"],
            "gl": [df_reg, df_res, df_total],
            "Suma_cuadrados": [ssr, sse, sst],
            "Promedio_cuadrados": [msr, mse, np.nan],
            "F": [f_stat, np.nan, np.nan],
            "Valor_critico_F": [f_crit_p, np.nan, np.nan],
        }
    )

    t_crit_05 = 1.96 if df_res > 30 else t_crit

    def _robusto(t_val: float) -> str:
        if t_val != t_val:
            return ""
        return "Sí" if abs(t_val) > t_crit_05 else "No"

    coeficientes = pd.DataFrame(
        {
            "": ["Intercepción (a)", f"{name_x} (pendiente b)"],
            "rol": ["intercepto_a", "pendiente_b"],
            "Coeficientes": [a, b],
            "Error_tipico": [se_a, se_b],
            "Estadistico_t": [t_a, t_b],
            "Probabilidad": [p_a, p_b],
            "Inferior_95": [ic_a[0], ic_b[0]],
            "Superior_95": [ic_a[1], ic_b[1]],
            "robusto_alpha_005": [_robusto(t_a), _robusto(t_b)],
            "nota": [
                "Término constante en Y = a + b·X",
                "Coeficiente de interés: efecto de X sobre Y (|t|>1,96 → robusto al 5%)",
            ],
        }
    )

    return OlsRegressionReport(
        estadisticos=estadisticos,
        anova=anova,
        coeficientes=coeficientes,
        variable_y=name_y,
        variable_x=name_x,
        n_obs=n,
    )


def reports_to_workbook_sheets(
    reports: list[OlsRegressionReport],
) -> dict[str, pd.DataFrame]:
    """Apila varias regresiones (una por ruta) en hojas únicas."""
    if not reports:
        return {}

    def _stack_tables(
        getter,
        title_col: str,
    ) -> pd.DataFrame:
        parts = []
        for rep in reports:
            header = pd.DataFrame(
                {
                    title_col: [
                        f"--- Regresión: {rep.variable_y} = a + b·{rep.variable_x} (n={rep.n_obs}) ---"
                    ]
                }
            )
            parts.append(header)
            parts.append(getter(rep))
            parts.append(pd.DataFrame({title_col: [""]}))
        return pd.concat(parts, ignore_index=True)

    notas = pd.DataFrame(
        {
            "concepto": [
                "Ecuación",
                "R²",
                "Pendiente b",
                "Significancia",
            ],
            "descripcion": [
                "Y = a + b·X (ej. Satisfaccion = 0,98 + 1,01·Calidad)",
                "R²: proporción de varianza de Y explicada por el modelo",
                "b: cambio en Y por cada unidad de X; hipótesis principal",
                "Robusto al 5% si |t| > 1,96 (aprox.) en Regresion_Coeficientes",
            ],
        }
    )

    return {
        "Regresion_Estadisticos": _stack_tables(lambda r: r.estadisticos, "Estadística"),
        "Regresion_ANOVA": _stack_tables(lambda r: r.anova, ""),
        "Regresion_Coeficientes": _stack_tables(lambda r: r.coeficientes, ""),
        "Regresion_Interpretacion": notas,
    }
