"""Criterios modernos e informe EQS."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.cbsem.fit_modern import (
    eqs_gof_summary_report,
    evaluate_fit_modern,
)


def test_modern_stricter_than_classic():
    metrics = {
        "chi2": 20.0,
        "DoF": 10.0,
        "chi2 p-value": 0.10,
        "CFI": 0.92,
        "TLI": 0.91,
        "RMSEA": 0.07,
        "RMSR": 0.05,
    }
    ev = evaluate_fit_modern(metrics, n_samples=500, n_params=20, rmsr=0.05)
    cfi = ev.loc[ev["indice"] == "CFI", "cumple"].iloc[0]
    assert cfi == "No"  # 0.92 < 0.95


def test_eqs_report_has_chi_square():
    rep = eqs_gof_summary_report(
        {"chi2": 45.653, "DoF": 13, "chi2 p-value": 0.00002, "CFI": 0.98},
        n_samples=200,
    )
    assert "CHI-SQUARE" in rep["concepto"].values


@pytest.mark.slow
def test_modern_sheets_on_cb_run():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("examples missing")
    from sem_tool.cbsem.fit import run_cbsem

    r = run_cbsem(path)
    assert r.fit_evaluation_modern is not None
    assert r.eqs_gof_report is not None
