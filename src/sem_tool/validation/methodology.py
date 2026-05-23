"""Reglas metodológicas: constructos latentes, ítems, hipótesis, escalas."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from sem_tool.io import excel as xl

MIN_ITEMS_PER_CONSTRUCT = 3
MIN_OBSERVATIONS_PER_VARIABLE = 100
SHEET_HIPOTESIS = "Hipotesis"
SHEET_INDICADORES = "Indicadores"


@dataclass
class ValidationReport:
    errors: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        rows = [
            {**r, "nivel": "error"} for r in self.errors
        ] + [{**r, "nivel": "advertencia"} for r in self.warnings]
        if not rows:
            rows.append(
                {
                    "tipo": "ok",
                    "mensaje": "Cumple reglas mínimas de constructos e ítems.",
                    "nivel": "ok",
                }
            )
        return pd.DataFrame(rows)

    def raise_if_errors(self) -> None:
        if self.errors:
            msgs = "\n".join(f"- {e['mensaje']}" for e in self.errors)
            raise ValueError(f"Validación metodológica fallida:\n{msgs}")


def read_hipotesis(workbook_path: Path) -> Optional[pd.DataFrame]:
    try:
        df = xl.read_sheet(workbook_path, SHEET_HIPOTESIS)
        return df if not df.empty else None
    except ValueError:
        return None


def read_indicadores_catalog(workbook_path: Path) -> Optional[pd.DataFrame]:
    try:
        df = xl.read_sheet(workbook_path, SHEET_INDICADORES)
        return df if not df.empty else None
    except ValueError:
        return None


def get_min_observations(workbook_path: Path | None = None) -> int:
    """Mínimo de observaciones por variable (hoja Config o default 100)."""
    if workbook_path is not None:
        try:
            val = xl.read_config_value(
                workbook_path, "observaciones_minimas", MIN_OBSERVATIONS_PER_VARIABLE
            )
            return max(1, int(val))
        except (TypeError, ValueError):
            pass
    return MIN_OBSERVATIONS_PER_VARIABLE


def validate_data_for_model(
    data: pd.DataFrame,
    indicator_columns: Iterable[str],
    catalog: Optional[pd.DataFrame] = None,
    min_items: int = MIN_ITEMS_PER_CONSTRUCT,
    min_obs_per_variable: int = MIN_OBSERVATIONS_PER_VARIABLE,
) -> ValidationReport:
    """Valida microdatos: ≥n observaciones por variable, no dicotómicas."""
    report = ValidationReport()
    cols = [c for c in indicator_columns if c in data.columns]
    missing = [c for c in indicator_columns if c not in data.columns]
    if missing:
        report.errors.append(
            {
                "tipo": "datos",
                "mensaje": f"Ítems ausentes en hoja Datos: {missing}",
            }
        )

    n_listwise = int(data[cols].dropna(how="any").shape[0]) if cols else 0
    if n_listwise < min_obs_per_variable:
        report.errors.append(
            {
                "tipo": "muestra",
                "mensaje": (
                    f"Casos completos (listwise) n={n_listwise}. "
                    f"Se requieren al menos {min_obs_per_variable} observaciones "
                    "por cada variable analizada."
                ),
            }
        )
    elif n_listwise < 200:
        report.warnings.append(
            {
                "tipo": "muestra",
                "mensaje": (
                    f"n={n_listwise}: cumple mínimo ({min_obs_per_variable}), "
                    "pero para CB-SEM se recomienda n≥200."
                ),
            }
        )

    for col in cols:
        series = data[col].dropna()
        n_valid = len(series)
        if n_valid < min_obs_per_variable:
            report.errors.append(
                {
                    "tipo": "muestra",
                    "mensaje": (
                        f"Variable '{col}': n={n_valid} observaciones válidas. "
                        f"Mínimo requerido: {min_obs_per_variable} por variable."
                    ),
                }
            )
        elif n_valid < min_obs_per_variable + 50:
            report.warnings.append(
                {
                    "tipo": "muestra",
                    "mensaje": (
                        f"Variable '{col}': n={n_valid}. Cerca del mínimo "
                        f"({min_obs_per_variable}); se recomienda ampliar la muestra."
                    ),
                }
            )
        unique = sorted(series.unique())
        n_unique = len(unique)
        if n_unique <= 2:
            report.errors.append(
                {
                    "tipo": "escala",
                    "mensaje": (
                        f"Ítem '{col}': solo {n_unique} valores distintos. "
                        "No use variables dicotómicas; emplee escalas ordinales "
                        "(Likert 5/7 puntos) basadas en literatura."
                    ),
                }
            )
        elif n_unique <= 4:
            report.warnings.append(
                {
                    "tipo": "escala",
                    "mensaje": (
                        f"Ítem '{col}': escala con pocos puntos (n={n_unique}). "
                        "Se recomienda Likert de al menos 5 categorías."
                    ),
                }
            )
        if catalog is not None and _catalog_has_column(catalog, "indicador"):
            ind_col = _col_name(catalog, "indicador")
            ref_col = _col_name(catalog, "referencia")
            row = catalog.loc[catalog[ind_col].astype(str) == col]
            if row.empty:
                report.warnings.append(
                    {
                        "tipo": "literatura",
                        "mensaje": (
                            f"Ítem '{col}' no está en hoja Indicadores "
                            "(falta referencia bibliográfica del instrumento)."
                        ),
                    }
                )
            elif ref_col and pd.isna(row.iloc[0].get(ref_col)):
                report.warnings.append(
                    {
                        "tipo": "literatura",
                        "mensaje": f"Ítem '{col}': sin referencia bibliográfica registrada.",
                    }
                )

    return report


def validate_pls_model(
    blocks: dict[str, list[str]],
    paths: list[tuple[str, str]],
    hipotesis: Optional[pd.DataFrame] = None,
    min_items: int = MIN_ITEMS_PER_CONSTRUCT,
) -> ValidationReport:
    report = ValidationReport()
    for construct, items in blocks.items():
        if len(items) < min_items:
            report.errors.append(
                {
                    "tipo": "constructo",
                    "mensaje": (
                        f"Constructo '{construct}' (factor latente) tiene {len(items)} ítem(s). "
                        f"Se requieren al menos {min_items} indicadores por constructo."
                    ),
                }
            )

    if not paths:
        report.warnings.append(
            {
                "tipo": "hipotesis",
                "mensaje": "No hay rutas estructurales (ej. Calidad → Satisfacción).",
            }
        )

    _check_hypothesis_sheet(paths, hipotesis, report)
    return report


def validate_cb_model(
    factors: dict[str, list[str]],
    structural_paths: list[tuple[str, str]],
    hipotesis: Optional[pd.DataFrame] = None,
    min_items: int = MIN_ITEMS_PER_CONSTRUCT,
) -> ValidationReport:
    report = ValidationReport()
    for factor, items in factors.items():
        if len(items) < min_items:
            report.errors.append(
                {
                    "tipo": "factor",
                    "mensaje": (
                        f"Factor latente '{factor}' tiene {len(items)} ítem(s). "
                        f"Mínimo recomendado: {min_items} variables observadas por constructo."
                    ),
                }
            )

    for lhs, rhs in structural_paths:
        if lhs not in factors and lhs not in _all_items(factors):
            report.warnings.append(
                {
                    "tipo": "modelo",
                    "mensaje": f"Ruta '{rhs} → {lhs}': revise que use factores latentes definidos.",
                }
            )

    _check_hypothesis_sheet(
        structural_paths, hipotesis, report, origin_dest=(1, 0)
    )
    return report


def parse_cb_factors_from_syntax_rows(modelo: pd.DataFrame) -> tuple[dict[str, list[str]], list[tuple[str, str]]]:
    """Extrae factores e ítems desde Modelo_CB."""
    from sem_tool.spec.cb_syntax import _normalize_op

    factors: dict[str, list[str]] = {}
    paths: list[tuple[str, str]] = []
    col_map = {str(c).lower(): c for c in modelo.columns}

    for _, row in modelo.iterrows():
        lhs = _str(row.get(col_map.get("lhs", "lhs")))
        rhs = _str(row.get(col_map.get("rhs", "rhs")))
        tipo = _str(row.get(col_map.get("tipo", "tipo"))).lower()
        op_raw = _str(row.get(col_map.get("op", "op")))
        if not lhs or not rhs:
            continue
        op = _normalize_op(op_raw, tipo)
        if op == "=~":
            items = [p.strip() for p in re.split(r"\s*\+\s*", rhs) if p.strip()]
            factors.setdefault(lhs, []).extend(items)
        elif op == "~":
            paths.append((rhs, lhs))
    return factors, paths


def parse_pls_blocks_indicators(modelo: pd.DataFrame) -> tuple[dict[str, list[str]], list[tuple[str, str]]]:
    col_map = {str(c).lower(): c for c in modelo.columns}
    blocks: dict[str, list[str]] = {}
    paths: list[tuple[str, str]] = []
    c_col = col_map.get("constructo", "constructo")
    i_col = col_map.get("indicador", "indicador")
    o_col = col_map.get("ruta_origen", "ruta_origen")
    d_col = col_map.get("ruta_destino", "ruta_destino")

    for _, row in modelo.iterrows():
        lv = _str(row.get(c_col))
        mv = _str(row.get(i_col))
        origin = _str(row.get(o_col))
        dest = _str(row.get(d_col))
        if lv and mv:
            blocks.setdefault(lv, []).append(mv)
        if origin and dest:
            paths.append((origin, dest))
    return blocks, paths


def merge_validation_warnings(
    existing: pd.DataFrame, report: ValidationReport
) -> pd.DataFrame:
    extra = report.to_dataframe()
    if existing.empty or "tipo" not in existing.columns:
        return extra
    return pd.concat([existing, extra], ignore_index=True)


def _check_hypothesis_sheet(
    paths: list[tuple[str, str]],
    hipotesis: Optional[pd.DataFrame],
    report: ValidationReport,
    origin_dest: tuple[int, int] = (0, 1),
) -> None:
    if hipotesis is None or hipotesis.empty:
        if paths:
            report.warnings.append(
                {
                    "tipo": "hipotesis",
                    "mensaje": (
                        "Defina la hoja Hipotesis con la fundamentación bibliográfica "
                        "(origen, destino, referencia, argumento)."
                    ),
                }
            )
        return

    o_idx, d_idx = origin_dest
    col_map = {str(c).lower(): c for c in hipotesis.columns}
    for need in ("origen", "destino"):
        if need not in col_map:
            report.warnings.append(
                {
                    "tipo": "hipotesis",
                    "mensaje": f"Hoja Hipotesis: falta columna '{need}'.",
                }
            )
            return

    for origin, dest in paths:
        ocol = col_map["origen"]
        dcol = col_map["destino"]
        match = hipotesis[
            (hipotesis[ocol].astype(str) == origin)
            & (hipotesis[dcol].astype(str) == dest)
        ]
        if match.empty:
            report.warnings.append(
                {
                    "tipo": "hipotesis",
                    "mensaje": (
                        f"Ruta {origin} → {dest} no documentada en hoja Hipotesis."
                    ),
                }
            )
        elif "referencia" in col_map:
            ref = match.iloc[0].get(col_map["referencia"])
            if pd.isna(ref) or not str(ref).strip():
                report.warnings.append(
                    {
                        "tipo": "hipotesis",
                        "mensaje": (
                            f"Ruta {origin} → {dest}: sin referencia bibliográfica."
                        ),
                    }
                )


def _all_items(factors: dict[str, list[str]]) -> set[str]:
    items: set[str] = set()
    for v in factors.values():
        items.update(v)
    return items


def _str(val) -> str:
    if pd.isna(val):
        return ""
    return str(val).strip()


def _catalog_has_column(catalog: pd.DataFrame, name: str) -> bool:
    return name in [str(c).lower() for c in catalog.columns]


def _col_name(df: pd.DataFrame, name: str) -> Optional[str]:
    for c in df.columns:
        if str(c).lower() == name.lower():
            return c
    return None
