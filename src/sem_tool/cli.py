"""Command-line interface for sem-tool."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from sem_tool.cbsem.fit import export_cbsem, run_cbsem
from sem_tool.io import excel as xl
from sem_tool.plsem.estimate import export_plsem, run_plsem
from sem_tool.stats.descriptives import run_descriptives_for_workbook

app = typer.Typer(
    name="sem-tool",
    help="CB-SEM (EQS) y PLS-SEM (SmartPLS) con flujo Excel.",
    no_args_is_help=True,
)


class InitMode(str, Enum):
    cb = "cb"
    pls = "pls"
    both = "both"


@app.command("init")
def init_cmd(
    mode: InitMode = typer.Option(InitMode.both, "--mode", "-m", help="cb, pls o both"),
    output: Path = typer.Option(
        Path("plantilla_sem.xlsx"),
        "--output",
        "-o",
        help="Ruta del archivo Excel a crear",
    ),
    sample: bool = typer.Option(
        True,
        "--sample/--empty",
        help="Incluir 200 casos simulados Calidad→Satisfacción (use --empty solo encabezados)",
    ),
) -> None:
    """Crear plantilla Excel (por defecto con datos de ejemplo listos para analizar)."""
    xl.create_template(output, mode.value, include_sample=sample)
    if sample:
        typer.echo(
            f"Plantilla con datos de ejemplo (n=200): {output.resolve()}\n"
            "Siguiente: python3 -m sem_tool descriptivos "
            f"{output.name}  (o cb / pls / run-all)"
        )
    else:
        typer.echo(f"Plantilla vacía: {output.resolve()} — rellene hoja Datos antes de analizar.")


@app.command("descriptivos")
def descriptivos_cmd(
    workbook: Path = typer.Argument(..., help="Excel con hoja Datos"),
) -> None:
    """Calcular media, varianza y matriz de covarianzas (paso previo al SEM)."""
    if not workbook.exists():
        raise typer.BadParameter(f"No existe: {workbook}")
    result = run_descriptives_for_workbook(workbook)
    typer.echo(
        f"Descriptivos: n={result.n_casos}, variables={len(result.variables)}. "
        "Hojas: Descriptivos, Matriz_Covarianzas, Covarianzas_Pares, "
        "Matriz_Correlaciones, Medias"
    )


@app.command("cb")
def cb_cmd(
    workbook: Path = typer.Argument(..., help="Archivo .xlsx con Datos y Modelo_CB"),
) -> None:
    """Ejecutar CB-SEM (estilo EQS) y escribir resultados en el mismo Excel."""
    if not workbook.exists():
        raise typer.BadParameter(f"No existe: {workbook}")
    typer.echo(f"CB-SEM: {workbook}")
    result = run_cbsem(workbook)
    export_cbsem(workbook, result)
    typer.echo(
        "Regresion (R², pendiente b, t>1,96), Tipos_Variables, Fit_Indices"
    )


@app.command("pls")
def pls_cmd(
    workbook: Path = typer.Argument(..., help="Archivo .xlsx con Datos y Modelo_PLS"),
    bootstraps: Optional[int] = typer.Option(
        None, "--bootstraps", "-b", help="Iteraciones bootstrap (default: hoja Config o 5000)"
    ),
    processes: Optional[int] = typer.Option(
        None, "--processes", "-p", help="Procesos paralelos (debe dividir bootstraps)"
    ),
) -> None:
    """Ejecutar PLS-SEM (estilo SmartPLS) con bootstrap."""
    if not workbook.exists():
        raise typer.BadParameter(f"No existe: {workbook}")
    n_boot = bootstraps or int(xl.read_config_value(workbook, "bootstraps", 5000))
    n_proc = processes or int(xl.read_config_value(workbook, "procesos_bootstrap", 2))
    typer.echo(f"PLS-SEM: {workbook} (bootstrap={n_boot}, processes={n_proc})")
    result = run_plsem(workbook, bootstraps=n_boot, processes=n_proc)
    export_plsem(workbook, result)
    typer.echo(
        "Descriptivos + PLS: Matriz_Covarianzas, Outer_Loadings, Paths, "
        "Bootstraps, R2, AVE_CR, HTMT, ..."
    )


@app.command("run-all")
def run_all_cmd(
    workbook: Path = typer.Argument(..., help="Excel con Datos y modelos CB y/o PLS"),
    bootstraps: Optional[int] = typer.Option(None, "--bootstraps", "-b"),
    processes: Optional[int] = typer.Option(None, "--processes", "-p"),
) -> None:
    """Ejecutar CB y PLS si existen las hojas de modelo."""
    import openpyxl

    if not workbook.exists():
        raise typer.BadParameter(f"No existe: {workbook}")
    wb = openpyxl.load_workbook(workbook, read_only=True)
    sheets = set(wb.sheetnames)
    wb.close()

    if "Modelo_CB" in sheets:
        typer.echo("--- CB-SEM ---")
        result_cb = run_cbsem(workbook)
        export_cbsem(workbook, result_cb)
    else:
        typer.echo("Omitido CB: no hay hoja Modelo_CB")

    if "Modelo_PLS" in sheets:
        typer.echo("--- PLS-SEM ---")
        n_boot = bootstraps or int(xl.read_config_value(workbook, "bootstraps", 5000))
        n_proc = processes or int(xl.read_config_value(workbook, "procesos_bootstrap", 2))
        result_pls = run_plsem(workbook, bootstraps=n_boot, processes=n_proc)
        export_plsem(workbook, result_pls)
    else:
        typer.echo("Omitido PLS: no hay hoja Modelo_PLS")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
