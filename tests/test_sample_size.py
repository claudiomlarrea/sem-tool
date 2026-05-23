"""Tests minimum 100 observations per variable (default)."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.validation.methodology import (
    MIN_OBSERVATIONS_PER_VARIABLE,
    validate_data_for_model,
)


def test_default_minimum_is_100():
    assert MIN_OBSERVATIONS_PER_VARIABLE == 100


def test_rejects_fewer_than_100_per_variable():
    data = pd.DataFrame({f"CAL{i}": list(range(99)) for i in range(1, 4)})
    report = validate_data_for_model(data, ["CAL1", "CAL2", "CAL3"])
    assert any(e["tipo"] == "muestra" for e in report.errors)


def test_accepts_100_observations():
    data = pd.DataFrame({f"CAL{i}": list(range(100)) for i in range(1, 4)})
    report = validate_data_for_model(data, ["CAL1", "CAL2", "CAL3"])
    assert not report.errors
