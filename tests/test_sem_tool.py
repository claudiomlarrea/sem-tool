"""Basic tests for sem-tool."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.io.excel import create_template, read_data
from sem_tool.spec.cb_syntax import parse_modelo_cb
from sem_tool.spec.pls_blocks import parse_modelo_pls


def test_cb_syntax_parser():
    df = pd.DataFrame(
        [
            ["medicion", "F1", "MEAS", "x1 + x2", "", "1"],
            ["estructural", "F2", "REG", "F1", "", ""],
        ],
        columns=["tipo", "lhs", "op", "rhs", "label", "fixed"],
    )
    syntax = parse_modelo_cb(df)
    assert "=~" in syntax
    assert "F2 ~ F1" in syntax


def test_pls_blocks_parser():
    df = pd.DataFrame(
        [
            ["A", "i1", "A", "", ""],
            ["A", "i2", "A", "", ""],
            ["B", "j1", "A", "A", "B"],
        ],
        columns=["constructo", "indicador", "modo", "ruta_origen", "ruta_destino"],
    )
    spec = parse_modelo_pls(df)
    assert "A" in spec.constructs
    assert "B" in spec.constructs


def test_create_template_cb(tmp_path):
    out = tmp_path / "t.xlsx"
    create_template(out, "cb")
    assert out.exists()


@pytest.mark.slow
def test_cb_example_fit():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")
    from sem_tool.cbsem.fit import run_cbsem

    result = run_cbsem(path)
    assert not result.fit_indices.empty
    if "CFI" in result.fit_indices["indice"].values:
        cfi = float(
            result.fit_indices.loc[
                result.fit_indices["indice"] == "CFI", "valor"
            ].iloc[0]
        )
        assert 0 <= cfi <= 1.01


@pytest.mark.slow
def test_pls_example_loadings():
    path = ROOT / "examples" / "ejemplo_pls_negocio.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")
    from sem_tool.plsem.estimate import run_plsem

    result = run_plsem(path, bootstraps=100, processes=1)
    assert not result.outer_loadings.empty
    assert result.outer_loadings.shape[0] >= 3
