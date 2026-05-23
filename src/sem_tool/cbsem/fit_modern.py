"""
Criterios de ajuste modernos y informe estilo EQS (salida actualizada).

Referencias habituales post-Hu & Bentler (1999):
- Kline (2016). Principles and Practice of Structural Equation Modeling.
- Brown (2015). Confirmatory Factor Analysis for Applied Research.
- Hair et al. (2021). Partial Least Squares SEM (PLS-SEM).
"""

from __future__ import annotations

import pandas as pd


def fit_criteria_modern_catalog() -> pd.DataFrame:
    """Umbrales más exigentes que la lámina clásica (1990s)."""
    return pd.DataFrame(
        [
            {
                "indice": "χ² Satorra-Bentler p",
                "criterio_clasico": "p > 0.05",
                "criterio_moderno": "p > 0.05 (preferir SB si no hay normalidad)",
                "prioridad": "Alta",
            },
            {
                "indice": "CFI",
                "criterio_clasico": "> 0.90",
                "criterio_moderno": "≥ 0.95",
                "prioridad": "Alta",
            },
            {
                "indice": "TLI (NNFI)",
                "criterio_clasico": "> 0.90",
                "criterio_moderno": "≥ 0.95",
                "prioridad": "Alta",
            },
            {
                "indice": "RMSEA",
                "criterio_clasico": "< 0.08",
                "criterio_moderno": "≤ 0.06 (aceptable ≤ 0.08)",
                "prioridad": "Alta",
            },
            {
                "indice": "RMSR / SRMR",
                "criterio_clasico": "bajo",
                "criterio_moderno": "≤ 0.08",
                "prioridad": "Media",
            },
            {
                "indice": "χ² / gl",
                "criterio_clasico": "≤ 5",
                "criterio_moderno": "≤ 3 (más estricto)",
                "prioridad": "Media",
            },
            {
                "indice": "N",
                "criterio_clasico": "≥ 5×parámetros",
                "criterio_moderno": "≥ 10×parámetros; CB-SEM ideal N≥200",
                "prioridad": "Alta",
            },
        ]
    )


def evaluate_fit_modern(
    metrics: dict[str, float | None],
    n_samples: int,
    n_params: int,
    rmsr: float | None = None,
) -> pd.DataFrame:
    rows: list[dict] = []

    def row(indice: str, valor, criterio: str, cumple: str, nota: str = "") -> None:
        rows.append(
            {
                "indice": indice,
                "valor": valor,
                "criterio_moderno": criterio,
                "cumple": cumple,
                "nota": nota,
            }
        )

    p_sb = metrics.get("chi2_sb p-value")
    if p_sb is not None and p_sb == p_sb:
        row("χ² Satorra-Bentler (p)", p_sb, "p > 0.05", _yn(p_sb > 0.05), "Estimador robusto (EQS ROBUST)")

    p_ml = metrics.get("chi2 p-value")
    if p_ml is not None and p_ml == p_ml:
        row("χ² ML (p)", p_ml, "p > 0.05", _yn(p_ml > 0.05), "Sensible a N grande")

    cfi = metrics.get("CFI")
    if cfi is not None and cfi == cfi:
        row("CFI", cfi, "≥ 0.95", _yn(cfi >= 0.95))

    tli = metrics.get("TLI")
    if tli is not None and tli == tli:
        row("TLI", tli, "≥ 0.95", _yn(tli >= 0.95))

    rmsea = metrics.get("RMSEA")
    if rmsea is not None and rmsea == rmsea:
        cumple = "Sí" if rmsea <= 0.06 else ("Parcial" if rmsea <= 0.08 else "No")
        row("RMSEA", rmsea, "≤ 0.06", cumple)

    if rmsr is not None and rmsr == rmsr:
        row("RMSR", rmsr, "≤ 0.08", _yn(rmsr <= 0.08))

    chi2 = metrics.get("chi2")
    dof = metrics.get("DoF")
    if chi2 is not None and dof and dof > 0 and chi2 == chi2:
        normed = chi2 / dof
        row("χ² / gl", normed, "≤ 3", _yn(normed <= 3))

    if n_params > 0:
        row("N", n_samples, f"≥ {10 * n_params}", _yn(n_samples >= 10 * n_params), "Regla ML")
        row("N (CB-SEM)", n_samples, "≥ 200 recomendado", _yn(n_samples >= 200), "Muestra grande")

    df = pd.DataFrame(rows)
    if not df.empty:
        n_ok = (df["cumple"] == "Sí").sum()
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [
                        {
                            "indice": "RESUMEN",
                            "valor": f"{n_ok}/{len(df)}",
                            "criterio_moderno": "Criterios modernos cumplidos",
                            "cumple": "Sí" if n_ok >= len(df) * 0.75 else "Revisar",
                            "nota": "Use PLS-SEM (SmartPLS) si N es pequeño o el objetivo es predictivo",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return df


def eqs_gof_summary_report(
    metrics: dict[str, float | None],
    n_samples: int,
    method: str = "ML",
) -> pd.DataFrame:
    """Informe tipo EQS GOODNESS OF FIT SUMMARY (slides 37–38)."""
    chi2 = metrics.get("chi2")
    dof = metrics.get("DoF")
    p = metrics.get("chi2 p-value")
    chi2_sb = metrics.get("chi2_sb")
    p_sb = metrics.get("chi2_sb p-value")

    lines = [
        ("SECCIÓN", f"GOODNESS OF FIT SUMMARY FOR METHOD = {method}"),
        ("N casos", n_samples),
        ("", ""),
        ("CHI-SQUARE", chi2),
        ("DEGREES OF FREEDOM", dof),
        ("PROBABILITY VALUE (ML)", p),
        ("", ""),
    ]
    if chi2_sb is not None:
        lines.extend(
            [
                ("SATORRA-BENTLER SCALED CHI-SQUARE", chi2_sb),
                ("PROBABILITY VALUE (SB)", p_sb),
                ("", ""),
            ]
        )
    lines.extend(
        [
            ("FIT INDICES", "-----------"),
            ("NFI", metrics.get("NFI")),
            ("NNFI / TLI", metrics.get("TLI")),
            ("CFI", metrics.get("CFI")),
            ("GFI", metrics.get("GFI")),
            ("AGFI", metrics.get("AGFI")),
            ("RMSR", metrics.get("RMSR")),
            ("RMSEA", metrics.get("RMSEA")),
            ("AIC", metrics.get("AIC")),
            ("BIC", metrics.get("BIC")),
        ]
    )
    if chi2 is not None and dof and dof > 0:
        lines.append(("CHI-SQUARE / DF", chi2 / dof))

    return pd.DataFrame(lines, columns=["concepto", "valor"])


def enfoque_recomendado_moderno() -> pd.DataFrame:
    """Qué usar hoy: robust CB vs PLS."""
    return pd.DataFrame(
        [
            {
                "situacion": "Normalidad multivariada dudosa, CB-SEM",
                "recomendacion": "χ² Satorra-Bentler + CFI/TLI/RMSEA modernos",
                "sem_tool": "Criterios_Ajuste_Modernos, Informe_Ajuste_EQS",
            },
            {
                "situacion": "Muestra pequeña o modelo predictivo",
                "recomendacion": "PLS-SEM (SmartPLS): bootstrap, AVE, HTMT",
                "sem_tool": "sem-tool pls",
            },
            {
                "situacion": "Teoría covarianzas / tesis UIC",
                "recomendacion": "CB-SEM: S vs Σ, identificación, GL>0",
                "sem_tool": "sem-tool cb + hojas Frederic",
            },
            {
                "situacion": "Reporte para revisor",
                "recomendacion": "Informe EQS + criterios ≥0.95 / RMSEA≤0.06",
                "sem_tool": "Informe_Ajuste_EQS + Criterios_Ajuste_Modernos",
            },
        ]
    )


def _yn(ok: bool) -> str:
    return "Sí" if ok else "No"
