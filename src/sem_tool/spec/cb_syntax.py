"""Convert Modelo_CB sheet rows to semopy syntax."""

from __future__ import annotations

import re

import pandas as pd

from sem_tool.io.schema import CB_COLUMNS, SHEET_MODELO_CB, validate_columns

# Excel interpreta "=~" como fórmula; en plantillas usar MEAS / REG / COV.
OP_ALIASES = {
    "meas": "=~",
    "measurement": "=~",
    "medicion": "=~",
    "carga": "=~",
    "load": "=~",
    "reg": "~",
    "regresion": "~",
    "estructural": "~",
    "structural": "~",
    "cov": "~~",
    "covarianza": "~~",
}


def _normalize_op(op: str, tipo: str) -> str:
    raw = op.strip().lower()
    if raw in ("=~", "~", "~~"):
        return raw
    if raw in OP_ALIASES:
        return OP_ALIASES[raw]
    tipo_l = tipo.strip().lower()
    if tipo_l in ("medicion", "measurement", "meas"):
        return "=~"
    if tipo_l in ("estructural", "structural", "regresion", "reg"):
        return "~"
    if tipo_l in ("cov", "covarianza"):
        return "~~"
    if not raw or raw == "nan":
        raise ValueError(f"Operador vacío o inválido (tipo={tipo!r}). Use MEAS, REG o COV en Excel.")
    return op.strip()


def parse_modelo_cb(df: pd.DataFrame) -> str:
    validate_columns(df.columns, CB_COLUMNS, SHEET_MODELO_CB)
    lines: list[str] = []
    for _, row in df.iterrows():
        lhs = _clean(row["lhs"])
        rhs = _clean(row["rhs"])
        tipo = str(row.get("tipo", "")).strip().lower()
        op_raw = _clean(row["op"])
        if not lhs or not rhs:
            continue
        op = _normalize_op(op_raw, tipo)
        label = _clean(row.get("label", ""))
        fixed = row.get("fixed", "")

        if tipo == "cov":
            # residual covariance between lhs and rhs
            if op != "~~":
                op = "~~"
            line = f"{lhs} {op} {rhs}"
        else:
            rhs_expanded = _expand_rhs(rhs)
            line = f"{lhs} {op} {rhs_expanded}"

        if label:
            line += f" @{label}"
        if _is_fixed(fixed):
            if op == "=~":
                parts = [p.strip() for p in rhs_expanded.split("+")]
                parts[0] = f"1*{parts[0]}"
                line = f"{lhs} {op} " + " + ".join(parts)
            elif "@" not in line:
                line += " @1"

        lines.append(line)

    if not lines:
        raise ValueError("Modelo_CB no contiene ecuaciones válidas.")
    return "\n".join(lines)


def _expand_rhs(rhs: str) -> str:
    parts = [p.strip() for p in re.split(r"\s*\+\s*", rhs) if p.strip()]
    return " + ".join(parts)


def _clean(val) -> str:
    if pd.isna(val):
        return ""
    return str(val).strip()


def _is_fixed(val) -> bool:
    if pd.isna(val):
        return False
    try:
        if float(val) == 1.0:
            return True
    except (TypeError, ValueError):
        pass
    s = str(val).strip().lower()
    return s in ("1", "1.0", "true", "yes", "si", "sí", "fijo")


def check_identification_warnings(modelo_cb: pd.DataFrame) -> list[str]:
    """Regla 6: cada factor latente debe tener métrica fijada (carga o varianza)."""
    warnings: list[str] = []
    factors_fixed: set[str] = set()
    factors_all: set[str] = set()
    col_map = {str(c).lower(): c for c in modelo_cb.columns}
    tipo_col = col_map.get("tipo", "tipo")
    lhs_col = col_map.get("lhs", "lhs")
    op_col = col_map.get("op", "op")
    fixed_col = col_map.get("fixed", "fixed")

    for _, row in modelo_cb.iterrows():
        op_raw = str(row.get(op_col, "")).strip().upper()
        if op_raw not in ("MEAS", "=~", ""):
            continue
        lhs = str(row.get(lhs_col, "")).strip()
        if not lhs:
            continue
        factors_all.add(lhs)
        if _is_fixed(row.get(fixed_col, "")):
            factors_fixed.add(lhs)

    missing = factors_all - factors_fixed
    for f in sorted(missing):
        warnings.append(
            f"Regla 6: factor '{f}' sin métrica fijada. "
            f"Ponga fixed=1 en una fila MEAS de {f} (carga 1*primer ítem)."
        )
    return warnings
