"""3 ecuaciones, 4 incógnitas (caso 2 ítems)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sem_tool.cbsem.moment_equations import (
    build_two_item_system_report,
    moment_count_one_factor,
    solucion_cerrada_lambda1_fijo,
)


def test_slide_4_items_10_equations_8_unknowns():
    ecu, inc, gl = moment_count_one_factor(4)
    assert ecu == 10
    assert inc == 8
    assert gl == 2


def test_three_equations_four_unknowns():
    # Números ficticios tipo muestra
    v1, v2, cov = 2.0, 1.8, 0.9
    sol = solucion_cerrada_lambda1_fijo(v1, v2, cov, 1.0)
    assert sol.loc[sol["parametro"] == "θ₁", "valor"].iloc[0] == pytest.approx(1.0)
    assert sol.loc[sol["parametro"] == "λ₂", "valor"].iloc[0] == pytest.approx(0.9)
    assert sol.loc[sol["parametro"] == "Verif. Cov(1,2)", "restriccion"].iloc[0].endswith("OK")


@pytest.mark.slow
def test_system_sheets_from_example():
    path = ROOT / "examples" / "ejemplo_cb_academico.xlsx"
    if not path.exists():
        pytest.skip("Run scripts/build_examples.py first")
    from sem_tool.cbsem.fit import run_cbsem

    result = run_cbsem(path)
    assert result.moment_system_sheets is not None
    keys = result.moment_system_sheets.keys()
    assert any(k.startswith("Sistema_") for k in keys)
    sistema_key = next(k for k in keys if k.startswith("Sistema_"))
    eq = result.moment_system_sheets[sistema_key]
    assert len(eq) >= 3
    ident_key = next(k for k in keys if k.startswith("Identificacion_"))
    ident = result.moment_system_sheets[ident_key]
    n_ecu = int(ident.loc[ident["concepto"] == "Ecuaciones (momentos)", "cantidad"].iloc[0])
    n_inc = int(ident.loc[ident["concepto"] == "Incógnitas", "cantidad"].iloc[0])
    assert n_ecu - n_inc == int(
        ident.loc[ident["concepto"] == "Grados de libertad", "cantidad"].iloc[0]
    )


def test_build_report_keys():
    import pandas as pd

    cov = pd.DataFrame([[2.0, 0.9], [0.9, 1.8]], index=["a", "b"], columns=["a", "b"])
    rep = build_two_item_system_report(cov, "a", "b", 500)
    assert set(rep.keys()) == {
        "Sistema_3_Ecuaciones",
        "Identificacion_2_Items",
        "Solucion_lambda1_igual_1",
    }
