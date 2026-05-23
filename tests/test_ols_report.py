"""Tests Excel-style OLS regression tables."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.stats.ols_report import ols_simple_regression


def test_ols_matches_slide_structure():
    rng = np.random.default_rng(0)
    n = 100
    x = rng.normal(size=n)
    y = 0.98 + 1.0065 * x + rng.normal(scale=0.1, size=n)
    rep = ols_simple_regression(
        pd.Series(y), pd.Series(x), name_y="Y", name_x="Variable X 1"
    )
    assert rep.n_obs == 100
    assert "Coeficiente de determinación" in rep.estadisticos["Estadística"].iloc[1]
    assert list(rep.anova[""]) == ["Regresión", "Residuos", "Total"]
    coef = rep.coeficientes
    assert coef.loc[1, "Coeficientes"] == coef.loc[1, "Coeficientes"]  # slope exists
    assert abs(float(coef.loc[1, "Coeficientes"]) - 1.0) < 0.5
