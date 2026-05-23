"""Parches de compatibilidad plspm ↔ pandas 2.x (Streamlit Cloud / Python 3.11)."""

from __future__ import annotations

import pandas as pd
import statsmodels.api as sm


def apply_plspm_pandas_patch() -> None:
    """
    plspm usa path.loc[dv,] (coma final); en pandas 2.x eso rompe con
    ValueError: zip() argument 2 is longer than argument 1.
    """
    import plspm.inner_model as im

    if getattr(im.InnerModel, "_sem_tool_patched", False):
        return

    def _summary(dv, regression):
        summary = pd.DataFrame(
            0,
            columns=["from", "to", "estimate", "std error", "t", "p>|t|"],
            index=regression.params.index,
        )
        summary["to"] = dv
        summary["from"] = regression.params.index
        summary["estimate"] = regression.params
        summary["std error"] = regression.bse
        summary["t"] = regression.tvalues
        summary["p>|t|"] = regression.pvalues
        summary["index"] = summary["from"] + " -> " + summary["to"]
        return summary.drop(["const"]).reset_index(drop=True)

    def patched_init(self, path: pd.DataFrame, scores: pd.DataFrame):
        self._InnerModel__summaries = None
        self._InnerModel__r_squared = pd.Series(0.0, index=path.index, name="r_squared")
        self._InnerModel__r_squared_adj = pd.Series(
            0.0, index=path.index, name="r_squared_adj"
        )
        self._InnerModel__path_coefficients = pd.DataFrame(
            0.0, columns=path.columns, index=path.index
        )
        endogenous = path.sum(axis=1).astype(bool)
        self._InnerModel__endogenous = list(endogenous[endogenous].index)
        rows = scores.shape[0]
        for dv in self._InnerModel__endogenous:
            row = path.loc[dv]
            ivs = row[row == 1].index
            exogenous = sm.add_constant(scores.loc[:, ivs])
            regression = sm.OLS(scores.loc[:, dv], exogenous).fit()
            self._InnerModel__path_coefficients.loc[dv, ivs] = regression.params
            rsquared = regression.rsquared
            self._InnerModel__r_squared.loc[dv] = rsquared
            n_predictors = int(row.sum())
            self._InnerModel__r_squared_adj.loc[dv] = 1 - (1 - rsquared) * (
                rows - 1
            ) / (rows - n_predictors - 1)
            part = _summary(dv, regression)
            if self._InnerModel__summaries is None:
                self._InnerModel__summaries = part
            else:
                self._InnerModel__summaries = pd.concat(
                    [self._InnerModel__summaries, part]
                ).reset_index(drop=True)
        self._InnerModel__effects = im._effects(self._InnerModel__path_coefficients)

    patched_init._sem_tool_patched = True  # type: ignore[attr-defined]
    im.InnerModel.__init__ = patched_init  # type: ignore[method-assign]
    im.InnerModel._sem_tool_patched = True  # type: ignore[attr-defined]
