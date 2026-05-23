"""CB-SEM diagnostic warnings."""

from __future__ import annotations

import pandas as pd
from scipy import stats


def collect_warnings(
    data: pd.DataFrame,
    n_params: int,
    syntax_lines: int,
) -> pd.DataFrame:
    rows: list[dict] = []
    n = data.shape[0]
    p = data.shape[1]

    if n < 200:
        rows.append(
            {
                "tipo": "muestra",
                "mensaje": f"N={n} es pequeño para CB-SEM; se recomienda N>=200 (regla práctica).",
            }
        )

    if n_params > 0 and n < n_params * 5:
        rows.append(
            {
                "tipo": "identificacion",
                "mensaje": f"Relación observaciones/parámetros (N/params) puede ser baja: {n}/{n_params}.",
            }
        )

    try:
        if p >= 3:
            chi2, pval = _mardia_test(data)
            if pval < 0.05:
                rows.append(
                    {
                        "tipo": "normalidad",
                        "mensaje": (
                            f"Mardia (aprox.): chi2={chi2:.3f}, p={pval:.4f}. "
                            "Posible desviación de normalidad multivariada."
                        ),
                    }
                )
    except Exception as exc:
        rows.append(
            {"tipo": "normalidad", "mensaje": f"No se pudo calcular Mardia: {exc}"}
        )

    if syntax_lines < 2:
        rows.append(
            {"tipo": "modelo", "mensaje": "Modelo con muy pocas ecuaciones; revise Modelo_CB."}
        )

    if not rows:
        rows.append({"tipo": "ok", "mensaje": "Sin advertencias críticas."})
    return pd.DataFrame(rows)


def _mardia_test(data: pd.DataFrame) -> tuple[float, float]:
    """Simplified multivariate normality check via univariate skew/kurtosis mean."""
    skews = []
    kurts = []
    for col in data.columns:
        x = data[col].dropna().values
        if len(x) < 8:
            continue
        skews.append(stats.skew(x))
        kurts.append(stats.kurtosis(x, fisher=False))
    if not skews:
        return 0.0, 1.0
    stat = sum(abs(s) for s in skews) + sum(abs(k - 3) for k in kurts)
    # rough chi-square proxy
    df = len(skews) * 2
    pval = 1 - stats.chi2.cdf(stat, df=max(df, 1))
    return stat, pval
