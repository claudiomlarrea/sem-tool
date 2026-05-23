"""Orquestación de análisis SEM para CLI y Streamlit."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import openpyxl
import pandas as pd

from sem_tool.cbsem.fit import export_cbsem, run_cbsem
from sem_tool.io import excel as xl
from sem_tool.plsem.estimate import export_plsem, run_plsem
from sem_tool.stats.descriptives import run_descriptives_for_workbook

InitMode = Literal["cb", "pls", "both"]


@dataclass
class PipelineLog:
    step: str
    message: str
    level: str = "info"


@dataclass
class PipelineResult:
    workbook_path: Path
    logs: list[PipelineLog] = field(default_factory=list)
    sheets_run: list[str] = field(default_factory=list)

    def add(self, step: str, message: str, level: str = "info") -> None:
        self.logs.append(PipelineLog(step=step, message=message, level=level))


def create_template_bytes(
    mode: InitMode = "both",
    *,
    include_sample: bool = True,
) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "plantilla_sem.xlsx"
        xl.create_template(path, mode, include_sample=include_sample)
        return path.read_bytes()


def workbook_sheet_names(path: Path) -> set[str]:
    wb = openpyxl.load_workbook(path, read_only=True)
    names = set(wb.sheetnames)
    wb.close()
    return names


def read_sheet_preview(path: Path, sheet: str, max_rows: int = 25) -> pd.DataFrame:
    df = xl.read_sheet(path, sheet)
    return df.head(max_rows)


def run_pipeline(
    workbook_path: Path,
    *,
    descriptivos: bool = True,
    cb: bool | None = None,
    pls: bool | None = None,
    bootstraps: int = 500,
    processes: int = 2,
) -> PipelineResult:
    """Ejecuta descriptivos y, si aplica, CB y/o PLS sobre un Excel."""
    path = Path(workbook_path)
    result = PipelineResult(workbook_path=path)
    sheets = workbook_sheet_names(path)

    if cb is None:
        cb = "Modelo_CB" in sheets
    if pls is None:
        pls = "Modelo_PLS" in sheets

    if descriptivos:
        desc = run_descriptives_for_workbook(path)
        result.sheets_run.append("Descriptivos")
        result.add(
            "descriptivos",
            f"n={desc.n_casos}, variables={len(desc.variables)}",
        )

    if cb:
        if "Modelo_CB" not in sheets:
            result.add("cb", "Omitido: no hay hoja Modelo_CB", level="warning")
        else:
            cb_result = run_cbsem(path)
            export_cbsem(path, cb_result)
            result.sheets_run.extend(
                ["Fit_Indices", "Paths_Estandarizados", "Loadings"]
            )
            result.add("cb", "CB-SEM completado (EQS-style)")

    if pls:
        if "Modelo_PLS" not in sheets:
            result.add("pls", "Omitido: no hay hoja Modelo_PLS", level="warning")
        else:
            n_boot = bootstraps or int(xl.read_config_value(path, "bootstraps", 5000))
            n_proc = processes or int(
                xl.read_config_value(path, "procesos_bootstrap", 2)
            )
            pls_result = run_plsem(path, bootstraps=n_boot, processes=n_proc)
            export_plsem(path, pls_result)
            result.sheets_run.extend(
                ["Outer_Loadings", "Paths", "AVE_CR", "HTMT"]
            )
            result.add(
                "pls",
                f"PLS-SEM completado (bootstrap={n_boot}, processes={n_proc})",
            )

    return result


def copy_upload_to_workdir(upload_bytes: bytes, filename: str) -> Path:
    """Guarda bytes subidos en un directorio temporal y devuelve la ruta."""
    tmp = Path(tempfile.mkdtemp(prefix="sem_tool_"))
    safe_name = Path(filename).name or "estudio.xlsx"
    if not safe_name.lower().endswith(".xlsx"):
        safe_name += ".xlsx"
    dest = tmp / safe_name
    dest.write_bytes(upload_bytes)
    return dest


def cleanup_workdir(path: Path) -> None:
    parent = path.parent
    if parent.name.startswith("sem_tool_") and parent.is_dir():
        shutil.rmtree(parent, ignore_errors=True)
