"""Tests for methodology validation rules."""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.validation.methodology import (
    validate_cb_model,
    validate_data_for_model,
    validate_pls_model,
)


def test_rejects_dichotomous_item():
    data = pd.DataFrame({"CAL1": [0, 1, 0, 1, 0, 1] * 10, "CAL2": [1, 2, 3, 4, 5] * 12})
    report = validate_data_for_model(data, ["CAL1", "CAL2"])
    assert any(e["tipo"] == "escala" for e in report.errors)


def test_requires_three_items_per_construct():
    blocks = {"Calidad": ["CAL1", "CAL2"]}
    report = validate_pls_model(blocks, [("Calidad", "Satisfaccion")])
    assert any(e["tipo"] == "constructo" for e in report.errors)


def test_cb_three_items_ok():
    factors = {
        "Calidad": ["CAL1", "CAL2", "CAL3"],
        "Satisfaccion": ["SAT1", "SAT2", "SAT3"],
    }
    data = pd.DataFrame(
        {c: [1, 2, 3, 4, 5] * 20 for c in factors["Calidad"] + factors["Satisfaccion"]}
    )
    report = validate_cb_model(
        factors, [("Calidad", "Satisfaccion")], hipotesis=None
    )
    data_report = validate_data_for_model(
        data, factors["Calidad"] + factors["Satisfaccion"]
    )
    report.errors.extend(data_report.errors)
    assert not report.errors
