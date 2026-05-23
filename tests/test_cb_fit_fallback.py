"""CB-SEM row filtering must not use a DataFrame as a boolean mask."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def test_dropna_subset_not_dataframe_mask():
    data = pd.DataFrame({"a": [1, 2, None], "b": [3, None, 5], "x": [0, 0, 0]})
    items = ["a", "b"]
    with pytest.raises(ValueError, match="Boolean array expected"):
        _ = data[data[items].dropna(how="any")]
    clean = data.dropna(subset=items)
    assert len(clean) == 1
    assert clean.iloc[0]["a"] == 1.0
