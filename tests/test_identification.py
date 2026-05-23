"""Grados de libertad: momentos S vs parámetros."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.cbsem.identification import (
    covariance_moments_count,
    summarize_identification,
)


def test_covariance_moments_2x2_matrix():
    """Matriz 2×2: var₁, var₂, cov₁₂ → 3 datos."""
    n_var, n_cov, n_mom = covariance_moments_count(2)
    assert n_var == 2
    assert n_cov == 1
    assert n_mom == 3  # 2*(2+1)/2 = 2*3/2


def test_covariance_moments_five_items():
    n_var, n_cov, n_mom = covariance_moments_count(5)
    assert n_var == 5
    assert n_cov == 10  # 5*4/2
    assert n_mom == 15  # 5*6/2


def test_covariance_moments_three_items():
    n_var, n_cov, n_mom = covariance_moments_count(3)
    assert n_var == 3
    assert n_cov == 3
    assert n_mom == 6


@pytest.mark.slow
def test_identification_from_cb_example():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")

    from sem_tool.cbsem.fit import run_cbsem

    result = run_cbsem(path)
    assert result.identification_sheet is not None
    sheet = result.identification_sheet
    p = int(sheet.loc[sheet["concepto"] == "p (variables observadas en S)", "valor"].iloc[0])
    momentos = int(
        sheet.loc[sheet["concepto"] == "Momentos únicos (matriz S completa)", "valor"].iloc[0]
    )
    covs = int(sheet.loc[sheet["concepto"] == "Covarianzas únicas en S", "valor"].iloc[0])
    gl = int(sheet.loc[sheet["concepto"] == "Grados de libertad (GL)", "valor"].iloc[0])
    assert momentos == p * (p + 1) // 2
    assert covs == p * (p - 1) // 2
    assert gl == momentos - int(
        sheet.loc[sheet["concepto"] == "Parámetros libres estimados (t)", "valor"].iloc[0]
    )
    assert gl > 0
    dof_fit = result.fit_indices.loc[result.fit_indices["indice"] == "DoF", "valor"]
    if not dof_fit.empty:
        assert int(dof_fit.iloc[0]) == gl
