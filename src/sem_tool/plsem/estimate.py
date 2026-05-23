"""PLS-SEM estimation with plspm."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from plspm.plspm import Plspm

from sem_tool.plsem.plspm_compat import apply_plspm_pandas_patch
from sem_tool.io import excel as xl

apply_plspm_pandas_patch()
from sem_tool.io.schema import SHEET_MODELO_PLS
from sem_tool.plsem import metrics as met
from sem_tool.plsem.regression import pls_regression_table
from sem_tool.stats.ols_report import reports_to_workbook_sheets
from sem_tool.stats.structural_ols import ols_reports_from_scores
from sem_tool.spec.pls_blocks import parse_modelo_pls
from sem_tool.stats.descriptives import run_descriptives_for_workbook
from sem_tool.validation.methodology import (
    merge_validation_warnings,
    parse_pls_blocks_indicators,
    read_hipotesis,
    read_indicadores_catalog,
    get_min_observations,
    validate_data_for_model,
    validate_pls_model,
)


@dataclass
class PlsSemResult:
    outer_loadings: pd.DataFrame
    paths: pd.DataFrame
    bootstraps: pd.DataFrame
    r2: pd.DataFrame
    efectos_f2: pd.DataFrame
    ave_cr: pd.DataFrame
    fornell_larcker: pd.DataFrame
    htmt: pd.DataFrame
    vif: pd.DataFrame
    warnings: pd.DataFrame
    effects: pd.DataFrame
    regresion_structural: pd.DataFrame
    ols_sheets: dict[str, pd.DataFrame]


def run_plsem(
    workbook_path: Path,
    bootstraps: int = 5000,
    processes: int = 2,
) -> PlsSemResult:
    path = Path(workbook_path)
    data = xl.read_data(path)
    modelo = xl.read_sheet(path, SHEET_MODELO_PLS)
    blocks_pre, paths_pre = parse_pls_blocks_indicators(modelo)
    all_items = [it for items in blocks_pre.values() for it in items]
    run_descriptives_for_workbook(path, columns=all_items)
    catalog = read_indicadores_catalog(path)
    hipotesis = read_hipotesis(path)

    min_obs = get_min_observations(path)
    method_report = validate_pls_model(blocks_pre, paths_pre, hipotesis)
    data_report = validate_data_for_model(
        data, all_items, catalog, min_obs_per_variable=min_obs
    )
    method_report.errors.extend(data_report.errors)
    method_report.warnings.extend(data_report.warnings)
    method_report.raise_if_errors()

    spec = parse_modelo_pls(modelo)

    bootstraps, processes = _normalize_bootstrap(bootstraps, processes)
    if bootstraps < 100:
        bootstraps = 500

    model_data = data[all_items].dropna(how="any")
    n_cases = int(model_data.shape[0])
    use_bootstrap = n_cases >= 10
    if not use_bootstrap:
        bootstraps = 0

    pls = Plspm(
        data=model_data,
        config=spec.config,
        bootstrap=use_bootstrap,
        bootstrap_iterations=max(bootstraps, 100) if use_bootstrap else 100,
        processes=processes,
    )

    outer = pls.outer_model()
    path_coef = pls.path_coefficients()
    inner_summary = pls.inner_summary()
    effects = pls.effects()

    blocks = _blocks_from_config(spec.config)
    modes = {lv: spec.config.mode(lv).name for lv in blocks}

    ave_cr = met.compute_ave_cr(outer, blocks)
    fl = met.fornell_larcker(pls.scores(), ave_cr)
    htmt = met.htmt_matrix(model_data, blocks)
    f2 = met.f_squared_from_effects(effects, inner_summary)
    vif = met.vif_formative(model_data, blocks, modes)

    r2 = inner_summary.copy()
    if "type" in r2.columns:
        r2 = r2.rename(columns={"type": "tipo_lv"})

    boot_df = _bootstrap_tables(pls)
    warnings = _pls_warnings(data, bootstraps, processes, n_cases, use_bootstrap)
    warnings = merge_validation_warnings(warnings, method_report)

    paths_long = _path_matrix_to_long(path_coef)
    regresion = pls_regression_table(pls, inner_summary)

    paths_pairs = [(r["origen"], r["destino"]) for _, r in paths_long.iterrows()]
    ols_min = min(min_obs, max(10, n_cases))
    ols_reports = ols_reports_from_scores(pls.scores(), paths_pairs, min_n=ols_min)
    ols_sheets = reports_to_workbook_sheets(ols_reports)

    return PlsSemResult(
        outer_loadings=outer,
        paths=paths_long,
        bootstraps=boot_df,
        r2=r2,
        efectos_f2=f2,
        ave_cr=ave_cr,
        fornell_larcker=fl,
        htmt=htmt,
        vif=vif,
        warnings=warnings,
        effects=effects,
        regresion_structural=regresion,
        ols_sheets=ols_sheets,
    )


def export_plsem(workbook_path: Path, result: PlsSemResult) -> None:
    from sem_tool.plsem.smartpls_guide import sistema_smartpls_catalog

    sheets = {
        "Resumen_SmartPLS": sistema_smartpls_catalog(),
        "Outer_Loadings": result.outer_loadings,
        "Paths": result.paths,
        "Bootstraps": result.bootstraps,
        "R2": result.r2,
        "Efectos_f2": result.efectos_f2,
        "AVE_CR": result.ave_cr,
        "Fornell_Larcker": result.fornell_larcker,
        "HTMT": result.htmt,
        "VIF": result.vif,
        "Regresion_Structural": result.regresion_structural,
        "Warnings": result.warnings,
    }
    if result.ols_sheets:
        sheets.update(result.ols_sheets)
    xl.write_result_sheets(workbook_path, sheets)


def _blocks_from_config(config) -> dict[str, list[str]]:
    blocks = {}
    for lv in list(config.path().index):
        blocks[lv] = list(config.mvs(lv))
    return blocks


def _normalize_bootstrap(n: int, processes: int) -> tuple[int, int]:
    processes = max(1, processes)
    if n % processes != 0:
        n = n - (n % processes)
        if n < processes * 10:
            n = processes * 10
    return n, processes


def _bootstrap_tables(pls: Plspm) -> pd.DataFrame:
    try:
        boot = pls.bootstrap()
        paths = boot.paths()
        if paths is not None and not paths.empty:
            return paths
    except Exception:
        pass
    return pd.DataFrame({"nota": ["Bootstrap no disponible o falló"]})


def _path_matrix_to_long(path_coef: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dest in path_coef.index:
        for orig in path_coef.columns:
            val = path_coef.loc[dest, orig]
            if val and float(val) != 0:
                rows.append({"origen": orig, "destino": dest, "coeficiente": float(val)})
    return pd.DataFrame(rows)


def _pls_warnings(
    data: pd.DataFrame,
    bootstraps: int,
    processes: int,
    n_listwise: int,
    bootstrap_active: bool,
) -> pd.DataFrame:
    rows = []
    n = n_listwise
    if not bootstrap_active:
        rows.append(
            {
                "tipo": "bootstrap",
                "mensaje": (
                    f"n={n}<10: bootstrap PLS desactivado. "
                    "Use al menos 10 observaciones para significancia por bootstrap."
                ),
            }
        )
    if n < 100:
        rows.append(
            {
                "tipo": "muestra",
                "mensaje": f"N={n}: PLS tolera muestras menores, pero bootstrap es más estable con N>=100.",
            }
        )
    if bootstraps < 1000:
        rows.append(
            {
                "tipo": "bootstrap",
                "mensaje": f"bootstraps={bootstraps}; SmartPLS suele usar 5000.",
            }
        )
    rows.append(
        {
            "tipo": "config",
            "mensaje": f"Bootstrap con {bootstraps} iteraciones y {processes} proceso(s).",
        }
    )
    if not any(r["tipo"] == "muestra" for r in rows):
        rows.insert(0, {"tipo": "ok", "mensaje": "Ejecución PLS completada."})
    return pd.DataFrame(rows)
