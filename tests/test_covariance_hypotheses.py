"""Hipótesis λ₁λ₂ψ y λ²ψ+θ."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


from sem_tool.cbsem.fit import run_cbsem


@pytest.mark.slow
def test_same_factor_covariance_is_lambda_product():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")
    result = run_cbsem(path)
    assert result.decomposition is not None
    h = result.decomposition.hipotesis_covarianzas
    row = h[(h["variable_1"] == "CAL1") & (h["variable_2"] == "CAL2")].iloc[0]
    assert row["formula_tesis"] == "λ₁ × λ₂"
    assert row["formula_estimacion"] == "λ₁ × λ₂ × ψ"
    assert row["coincide_estimacion_con_modelo"] == "Sí"
    assert abs(float(row["producto_tesis"]) - float(row["lambda_1"]) * float(row["lambda_2"])) < 1e-6
    assert abs(float(row["producto_estimacion"]) - float(row["valor_Sigma_modelo"])) < 1e-4


@pytest.mark.slow
def test_variance_is_lambda_sq_plus_theta():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")
    result = run_cbsem(path)
    h = result.decomposition.hipotesis_covarianzas
    row = h[(h["variable_1"] == "CAL1") & (h["variable_2"] == "CAL1")].iloc[0]
    assert "λ² + σ" in row["formula_tesis"]
    assert row["coincide_estimacion_con_modelo"] == "Sí"
    tesis = float(row["producto_tesis"])
    assert abs(tesis - float(row["lambda_1"]) ** 2 - float(row["sigma_error"])) < 1e-6


@pytest.mark.slow
def test_sigma_tesis_matrix_exported():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")
    result = run_cbsem(path)
    d = result.decomposition
    assert not d.sigma_tesis.empty
    h = d.hipotesis_covarianzas
    row = h[(h["variable_1"] == "CAL1") & (h["variable_2"] == "CAL2")].iloc[0]
    assert d.sigma_tesis.loc["CAL1", "CAL2"] == pytest.approx(float(row["producto_tesis"]), rel=1e-6)
    var_row = h[(h["variable_1"] == "CAL1") & (h["variable_2"] == "CAL1")].iloc[0]
    assert d.sigma_tesis.loc["CAL1", "CAL1"] == pytest.approx(float(var_row["producto_tesis"]), rel=1e-6)
