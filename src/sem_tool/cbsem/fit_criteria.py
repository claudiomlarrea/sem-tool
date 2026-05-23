"""
Criterios de ajuste del modelo (diapositiva «The logic of the model fitness»).

Referencia: Hu & Bentler (1999), Structural Equation Modeling 6(1):1-55.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def fit_criteria_catalog() -> pd.DataFrame:
    """Tabla didáctica = lámina (absolutos, incrementales, parsimoniosos)."""
    return pd.DataFrame(
        [
            {
                "tipo": "Absoluto",
                "indice": "χ² y p-valor",
                "criterio": "p > 0.05",
                "destacado": "Sí",
                "nota": "No rechazar el modelo por χ²",
            },
            {
                "tipo": "Absoluto",
                "indice": "χ² Satorra-Bentler y p",
                "criterio": "p > 0.05",
                "destacado": "Sí",
                "nota": "Robusto ante no normalidad",
            },
            {
                "tipo": "Absoluto",
                "indice": "GFI",
                "criterio": "> 0.90",
                "destacado": "",
                "nota": "Goodness of Fit Index",
            },
            {
                "tipo": "Absoluto",
                "indice": "RMSR",
                "criterio": "Bajo (cercano a 0)",
                "destacado": "",
                "nota": "Root Mean Squared Residual",
            },
            {
                "tipo": "Absoluto",
                "indice": "RMSEA",
                "criterio": "< 0.08",
                "destacado": "Sí",
                "nota": "Error de aproximación; también < 0.05 excelente",
            },
            {
                "tipo": "Incremental",
                "indice": "NFI (Δ)",
                "criterio": "> 0.90",
                "destacado": "",
                "nota": "Normed Fit Index",
            },
            {
                "tipo": "Incremental",
                "indice": "NNFI / TLI (Δ)",
                "criterio": "> 0.90",
                "destacado": "",
                "nota": "Non-Normed Fit Index",
            },
            {
                "tipo": "Incremental",
                "indice": "AGFI",
                "criterio": "> 0.90",
                "destacado": "",
                "nota": "Adjusted GFI",
            },
            {
                "tipo": "Incremental",
                "indice": "CFI (Δ)",
                "criterio": "> 0.90 (ideal > 0.95)",
                "destacado": "Sí",
                "nota": "Comparative Fit Index",
            },
            {
                "tipo": "Parsimonioso",
                "indice": "χ² / gl",
                "criterio": "≤ 5",
                "destacado": "Sí",
                "nota": "Chi-cuadrado normado; gl = grados de libertad",
            },
            {
                "tipo": "Muestra",
                "indice": "Tamaño muestral N",
                "criterio": "N ≥ 5 × parámetros (Hu & Bentler)",
                "destacado": "",
                "nota": "PPT también cita N ≥ 10 × parámetros (regla práctica ML)",
            },
        ]
    )


def rmsr_from_matrices(observed: pd.DataFrame, implied: pd.DataFrame) -> float:
    """RMSR a partir de S y Σ (residual = S − Σ)."""
    diff = observed.astype(float) - implied.astype(float)
    p = diff.shape[0]
    sq = []
    cols = list(diff.columns)
    for i in range(p):
        for j in range(i, p):
            sq.append(float(diff.iloc[i, j]) ** 2)
    if not sq:
        return float("nan")
    return float(np.sqrt(np.mean(sq)))


def evaluate_fit_indices(
    metrics: dict[str, float | None],
    n_samples: int,
    n_params: int,
    rmsr: float | None = None,
) -> pd.DataFrame:
    """Evalúa índices calculados frente a criterios de la diapositiva."""
    rows: list[dict] = []

    def add(
        tipo: str,
        indice: str,
        valor,
        criterio: str,
        cumple: str,
        destacado: str = "",
    ) -> None:
        rows.append(
            {
                "tipo_ajuste": tipo,
                "indice": indice,
                "valor": valor,
                "criterio_referencia": criterio,
                "cumple": cumple,
                "destacado_lamina": destacado,
            }
        )

    chi2 = metrics.get("chi2")
    dof = metrics.get("DoF")
    p = metrics.get("chi2 p-value")
    if p is not None and p == p:
        add("Absoluto", "χ² p-valor", p, "p > 0.05", _yes_no(p > 0.05), "Sí")

    chi2_sb = metrics.get("chi2_sb")
    p_sb = metrics.get("chi2_sb p-value")
    if p_sb is not None and p_sb == p_sb:
        add("Absoluto", "χ² Satorra-Bentler p", p_sb, "p > 0.05", _yes_no(p_sb > 0.05), "Sí")

    gfi = metrics.get("GFI")
    if gfi is not None and gfi == gfi:
        add("Absoluto", "GFI", gfi, "> 0.90", _yes_no(gfi > 0.90))

    if rmsr is not None and rmsr == rmsr:
        add("Absoluto", "RMSR", rmsr, "Bajo (< 0.08 orientativo)", _yes_no(rmsr < 0.08))

    rmsea = metrics.get("RMSEA")
    if rmsea is not None and rmsea == rmsea:
        add("Absoluto", "RMSEA", rmsea, "< 0.08", _yes_no(rmsea < 0.08), "Sí")

    nfi = metrics.get("NFI")
    if nfi is not None and nfi == nfi:
        add("Incremental", "NFI", nfi, "> 0.90", _yes_no(nfi > 0.90))

    tli = metrics.get("TLI")
    if tli is not None and tli == tli:
        add("Incremental", "NNFI / TLI", tli, "> 0.90", _yes_no(tli > 0.90))

    agfi = metrics.get("AGFI")
    if agfi is not None and agfi == agfi:
        add("Incremental", "AGFI", agfi, "> 0.90", _yes_no(agfi > 0.90))

    cfi = metrics.get("CFI")
    if cfi is not None and cfi == cfi:
        cumple = "Sí" if cfi > 0.95 else ("Parcial" if cfi > 0.90 else "No")
        add("Incremental", "CFI", cfi, "> 0.90 (ideal > 0.95)", cumple, "Sí")

    if chi2 is not None and dof is not None and dof > 0 and chi2 == chi2:
        normado = chi2 / dof
        add("Parsimonioso", "χ² / gl", normado, "≤ 5", _yes_no(normado <= 5), "Sí")

    min_n5 = 5 * n_params if n_params > 0 else 0
    min_n10 = 10 * n_params if n_params > 0 else 0
    if n_params > 0:
        add(
            "Muestra",
            "N vs 5×parámetros",
            n_samples,
            f"N ≥ {min_n5} (Hu & Bentler)",
            _yes_no(n_samples >= min_n5),
        )
        add(
            "Muestra",
            "N vs 10×parámetros",
            n_samples,
            f"N ≥ {min_n10} (PPT Frederic, ML)",
            _yes_no(n_samples >= min_n10),
        )

    if chi2 is not None and dof is not None and dof > 0 and chi2 == chi2:
        add(
            "Interpretación",
            "H₀: modelo ajusta (S≈Σ)",
            p if p is not None else None,
            "p > 0.05 → no rechazar H₀",
            _yes_no(p is not None and p > 0.05) if p is not None else "—",
        )

    return pd.DataFrame(rows)


def _yes_no(ok: bool) -> str:
    return "Sí" if ok else "No"


def collect_metrics_for_evaluation(model, cov_observed: pd.DataFrame | None) -> tuple[dict, float | None]:
    """Lee índices de semopy y RMSR si hay matriz observada."""
    from semopy.stats import (
        __get_chi2_base,
        calc_agfi,
        calc_chi2,
        calc_chi2_sb,
        calc_cfi,
        calc_dof,
        calc_gfi,
        calc_nfi,
        calc_rmsea,
        calc_tli,
    )

    dof = int(calc_dof(model))
    chi2, chi2_p = calc_chi2(model, dof)
    chi2_base, dof_base = __get_chi2_base(model)
    gfi = float(calc_gfi(model, chi2, chi2_base))
    metrics: dict[str, float | None] = {
        "DoF": float(dof),
        "chi2": float(chi2),
        "chi2 p-value": float(chi2_p),
        "CFI": float(calc_cfi(model, dof, chi2, dof_base, chi2_base)),
        "TLI": float(calc_tli(model, dof, chi2, dof_base, chi2_base)),
        "RMSEA": float(calc_rmsea(model, chi2, dof)),
        "GFI": gfi,
        "AGFI": float(calc_agfi(model, dof, dof_base, gfi)),
        "NFI": float(calc_nfi(model, chi2, chi2_base)),
    }
    try:
        chi2_sb, p_sb = calc_chi2_sb(model, dof)
        metrics["chi2_sb"] = float(chi2_sb)
        metrics["chi2_sb p-value"] = float(p_sb)
    except Exception:
        pass

    rmsr = None
    if cov_observed is not None:
        try:
            obs_names = list(model.vars["observed"])
            S = cov_observed.loc[obs_names, obs_names]
            sigma_np, _ = model.calc_sigma()
            sigma = pd.DataFrame(sigma_np, index=obs_names, columns=obs_names)
            rmsr = rmsr_from_matrices(S, sigma)
            metrics["RMSR"] = rmsr
        except Exception:
            pass
    return metrics, rmsr
