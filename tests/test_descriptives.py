"""Tests for descriptive statistics and covariance matrix."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.stats.descriptives import compute_descriptives


def test_mean_variance_covariance():
    rng = np.random.default_rng(1)
    df = pd.DataFrame(
        {
            "CAL1": rng.integers(1, 6, 50),
            "CAL2": rng.integers(1, 6, 50),
            "CAL3": rng.integers(1, 6, 50),
        }
    )
    result = compute_descriptives(df)
    assert result.n_casos == 50
    assert abs(result.descriptivos.loc[0, "media"] - df["CAL1"].mean()) < 1e-9
    assert abs(result.descriptivos.loc[0, "varianza"] - df["CAL1"].var(ddof=1)) < 1e-9
    assert result.covarianza.shape == (3, 3)
    assert abs(result.covarianza.loc["CAL1", "CAL2"] - df["CAL1"].cov(df["CAL2"])) < 1e-9
    pair = result.covarianzas_pares.query(
        "variable_1=='CAL1' & variable_2=='CAL2'"
    )
    assert abs(pair.iloc[0]["covarianza"] - result.covarianza.loc["CAL1", "CAL2"]) < 1e-9


def test_export_descriptives_workbook(tmp_path):
    from sem_tool.stats.descriptives import run_descriptives_for_workbook

    path = tmp_path / "d.xlsx"
    df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 3, 4, 5, 6]})
    df.to_excel(path, sheet_name="Datos", index=False)
    run_descriptives_for_workbook(path)
    cov = pd.read_excel(path, sheet_name="Matriz_Covarianzas", index_col=0)
    desc = pd.read_excel(path, sheet_name="Descriptivos")
    assert cov.shape == (2, 2)
    assert "media" in desc.columns
    assert "observaciones" in desc.columns
    assert "varianza" in desc.columns
