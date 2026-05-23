"""PLS-SEM construct metrics: AVE, CR, HTMT, Fornell-Larcker, f², VIF."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_ave_cr(
    outer_model: pd.DataFrame,
    blocks: dict[str, list[str]],
) -> pd.DataFrame:
    """AVE and composite reliability per reflective block."""
    rows = []
    load_col = "loading" if "loading" in outer_model.columns else outer_model.columns[-1]
    for lv, indicators in blocks.items():
        inds = [i for i in indicators if i in outer_model.index]
        if not inds:
            continue
        loadings = outer_model.loc[inds, load_col].astype(float).values
        loadings = np.abs(loadings)
        ave = float(np.mean(loadings**2))
        s = float(np.sum(loadings)) ** 2
        d = s + float(np.sum(1 - loadings**2))
        cr = s / d if d > 0 else np.nan
        rows.append({"constructo": lv, "AVE": ave, "CR": cr, "n_indicadores": len(inds)})
    return pd.DataFrame(rows)


def _mean_abs_upper_triangle(corr_block: pd.DataFrame) -> float:
    """Mean of absolute correlations in the upper triangle (excl. diagonal)."""
    arr = corr_block.abs().to_numpy(dtype=float)
    n = arr.shape[0]
    if n < 2:
        return np.nan
    i, j = np.triu_indices(n, k=1)
    vals = arr[i, j]
    if vals.size == 0:
        return np.nan
    return float(np.mean(vals))


def fornell_larcker(scores: pd.DataFrame, ave_cr: pd.DataFrame) -> pd.DataFrame:
    """Square root AVE on diagonal; latent correlations off-diagonal."""
    lvs = list(scores.columns)
    corr = scores.corr()
    fl = corr.copy()
    for lv in lvs:
        row = ave_cr.loc[ave_cr["constructo"] == lv, "AVE"]
        if not row.empty and row.iloc[0] > 0:
            fl.loc[lv, lv] = np.sqrt(row.iloc[0])
    return fl


def htmt_matrix(data: pd.DataFrame, blocks: dict[str, list[str]]) -> pd.DataFrame:
    """Heterotrait-Monotrait ratio between construct pairs."""
    lvs = list(blocks.keys())
    mat = pd.DataFrame(np.nan, index=lvs, columns=lvs)
    cor = data.corr()
    for i, lv_a in enumerate(lvs):
        for j, lv_b in enumerate(lvs):
            if i >= j:
                continue
            inds_a = [x for x in blocks[lv_a] if x in cor.columns]
            inds_b = [x for x in blocks[lv_b] if x in cor.columns]
            if not inds_a or not inds_b:
                continue
            hetero = cor.loc[inds_a, inds_b].abs().mean().mean()
            ma = _mean_abs_upper_triangle(cor.loc[inds_a, inds_a])
            mb = _mean_abs_upper_triangle(cor.loc[inds_b, inds_b])
            denom = np.sqrt(ma * mb) if ma > 0 and mb > 0 else np.nan
            val = hetero / denom if denom and not np.isnan(denom) else np.nan
            mat.loc[lv_a, lv_b] = val
            mat.loc[lv_b, lv_a] = val
    np.fill_diagonal(mat.values, np.nan)
    return mat


def f_squared_from_effects(effects: pd.DataFrame, inner_summary: pd.DataFrame) -> pd.DataFrame:
    """Cohen f² for endogenous constructs from R² and path effects."""
    rows = []
    r2_col = None
    for c in inner_summary.columns:
        if "r_squared" in str(c).lower() or c.lower() in ("r_squared", "r2", "r²"):
            r2_col = c
            break
    if r2_col is None and len(inner_summary.columns) >= 2:
        r2_col = inner_summary.columns[1]

    for lv in inner_summary.index:
        r2 = float(inner_summary.loc[lv, r2_col]) if r2_col else np.nan
        f2 = (r2 / (1 - r2)) if r2 and r2 < 1 else np.nan
        size = _effect_size_label(f2)
        rows.append({"constructo_endogeno": lv, "R2": r2, "f2": f2, "tamano_efecto": size})
    return pd.DataFrame(rows)


def vif_formative(data: pd.DataFrame, blocks: dict[str, list[str]], modes: dict[str, str]) -> pd.DataFrame:
    """VIF for formative (mode B) indicators."""
    rows = []
    for lv, indicators in blocks.items():
        if modes.get(lv, "A") != "B":
            continue
        inds = [i for i in indicators if i in data.columns]
        if len(inds) < 2:
            continue
        X = data[inds].dropna()
        for col in inds:
            others = [c for c in inds if c != col]
            y = X[col]
            Xo = X[others]
            Xo = np.column_stack([np.ones(len(Xo)), Xo.values])
            beta, _, _, _ = np.linalg.lstsq(Xo, y.values, rcond=None)
            yhat = Xo @ beta
            ss_res = np.sum((y.values - yhat) ** 2)
            ss_tot = np.sum((y.values - y.mean()) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
            vif = 1 / (1 - r2) if r2 < 1 else np.inf
            rows.append({"constructo": lv, "indicador": col, "VIF": vif})
    return pd.DataFrame(rows)


def _effect_size_label(f2: float) -> str:
    if np.isnan(f2):
        return ""
    if f2 >= 0.35:
        return "large"
    if f2 >= 0.15:
        return "medium"
    if f2 >= 0.02:
        return "small"
    return "negligible"
