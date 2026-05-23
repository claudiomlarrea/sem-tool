"""Thin wrapper around io.excel write helpers."""

from pathlib import Path

from sem_tool.cbsem.fit import CbSemResult, export_cbsem
from sem_tool.plsem.estimate import PlsSemResult, export_plsem


def write_cb_results(workbook: Path, result: CbSemResult) -> None:
    export_cbsem(workbook, result)


def write_pls_results(workbook: Path, result: PlsSemResult) -> None:
    export_plsem(workbook, result)
