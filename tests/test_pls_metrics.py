"""Tests for PLS construct metrics."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.plsem import metrics as met


def test_mean_abs_upper_triangle_ignores_diagonal():
    block = pd.DataFrame(
        [[1.0, 0.6, 0.3], [0.6, 1.0, 0.4], [0.3, 0.4, 1.0]],
        index=["a", "b", "c"],
        columns=["a", "b", "c"],
    )
    assert met._mean_abs_upper_triangle(block) == pytest.approx(0.4333333333)


def test_htmt_matrix_no_pandas_where_mask_error():
    rng = np.random.default_rng(42)
    n = 120
    cal = rng.normal(size=(n, 3))
    sat = cal @ np.array([0.5, 0.4, 0.3]) + rng.normal(scale=0.5, size=n)
    data = pd.DataFrame(
        {
            "CAL1": cal[:, 0],
            "CAL2": cal[:, 1],
            "CAL3": cal[:, 2],
            "SAT1": sat + rng.normal(scale=0.2, size=n),
            "SAT2": sat + rng.normal(scale=0.2, size=n),
            "SAT3": sat + rng.normal(scale=0.2, size=n),
        }
    )
    blocks = {"Calidad": ["CAL1", "CAL2", "CAL3"], "Satisfaccion": ["SAT1", "SAT2", "SAT3"]}
    htmt = met.htmt_matrix(data, blocks)
    assert htmt.shape == (2, 2)
    assert np.isfinite(htmt.loc["Calidad", "Satisfaccion"])
