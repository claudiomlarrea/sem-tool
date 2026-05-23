"""Criterios de ajuste (lámina model fitness)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.cbsem.fit_criteria import evaluate_fit_indices, fit_criteria_catalog


def test_catalog_has_three_types():
    cat = fit_criteria_catalog()
    assert "Absoluto" in cat["tipo"].values
    assert "Incremental" in cat["tipo"].values
    assert "Parsimonioso" in cat["tipo"].values


def test_evaluate_chi2_normado():
    ev = evaluate_fit_indices(
        {"chi2": 10.0, "DoF": 2, "CFI": 0.95, "RMSEA": 0.05, "GFI": 0.92},
        n_samples=500,
        n_params=8,
    )
    row = ev.loc[ev["indice"] == "χ² / gl"].iloc[0]
    assert float(row["valor"]) == pytest.approx(5.0)
    assert row["cumple"] == "Sí"


@pytest.mark.slow
def test_criterios_ajuste_sheet_exported():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")
    from sem_tool.cbsem.fit import run_cbsem

    result = run_cbsem(path)
    assert result.fit_evaluation is not None
    assert not result.fit_evaluation.empty
    assert "CFI" in result.fit_evaluation["indice"].values
