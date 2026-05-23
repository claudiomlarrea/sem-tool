"""Tests structural regression R2 and slope."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.cbsem.regression import structural_regression_table
from sem_tool.cbsem.fit import run_cbsem


def test_cb_regression_has_slope_and_r2():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        return
    result = run_cbsem(path)
    reg = result.decomposition.regresion_structural
    row = reg.loc[reg["variable_dependiente_Y"] == "Satisfaccion"].iloc[0]
    assert row["variable_independiente_X"] == "Calidad"
    assert float(row["pendiente_b"]) != 0
    assert 0 <= float(row["R2"]) <= 1
