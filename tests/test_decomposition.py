"""Tests DATA = MODEL + RESIDUAL decomposition."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.cbsem.fit import run_cbsem


def test_decomposition_sheets_exist():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        return
    result = run_cbsem(path)
    assert result.decomposition is not None
    d = result.decomposition
    assert d.observada.shape == d.implicita.shape == d.residual.shape
    import numpy as np

    diff = d.observada.values - d.implicita.values - d.residual.values
    assert np.allclose(diff, 0, atol=1e-6)
    assert not result.decomposition.ecuaciones.empty
