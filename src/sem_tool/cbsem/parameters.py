"""Listado de parámetros estimados vs fijados (reglas 1–6)."""

from __future__ import annotations

import pandas as pd
from semopy import Model
from semopy.inspector import inspect_list


def parameters_report(model: Model) -> pd.DataFrame:
    """Tabla de parámetros libres y fijados según salida semopy."""
    try:
        ins = inspect_list(model, information=None, std_est=False)
    except Exception:
        return pd.DataFrame({"nota": ["Parámetros no disponibles"]})

    if ins is None or ins.empty:
        return pd.DataFrame({"nota": ["Sin parámetros estimados"]})

    rows = []
    for _, row in ins.iterrows():
        op = str(row.get("op", ""))
        regla = _rule_for_op(op)
        rows.append(
            {
                "operacion": op,
                "lhs": row.get("lval", ""),
                "rhs": row.get("rval", ""),
                "estimado": row.get("Estimate", ""),
                "regla_sem": regla,
                "es_parametro_libre": "Sí" if regla and "Nunca" not in regla else "Derivado",
            }
        )
    return pd.DataFrame(rows)


def _rule_for_op(op: str) -> str:
    if op == "=~":
        return "Regla 3 (carga); Regla 6 si hay @1 o 1*"
    if op == "~":
        return "Regla 4 (regresión)"
    if op == "~~":
        return "Regla 1/2 (varianza o covarianza exógena)"
    return ""
