"""CB-SEM estimation with semopy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from semopy import Model
from semopy.inspector import inspect_matrices
from semopy.stats import (
    __get_chi2_base,
    calc_agfi,
    calc_aic,
    calc_bic,
    calc_chi2,
    calc_cfi,
    calc_dof,
    calc_gfi,
    calc_likelihood,
    calc_nfi,
    calc_rmsea,
    calc_tli,
)

from sem_tool.cbsem.decomposition import CovarianceDecomposition, decompose_covariance
from sem_tool.cbsem.errors import export_error_tables
from sem_tool.cbsem.identification import (
    append_fit_identification_rows,
    identification_report,
    identification_warnings,
)
from sem_tool.cbsem.parameters import parameters_report
from sem_tool.cbsem.diagnostics import collect_warnings
from sem_tool.io import excel as xl
from sem_tool.io.schema import SHEET_MODELO_CB
from sem_tool.spec.cb_syntax import parse_modelo_cb
from sem_tool.stats.descriptives import (
    compute_descriptives,
    export_descriptives_to_workbook,
)
from sem_tool.stats.ols_report import reports_to_workbook_sheets
from sem_tool.stats.structural_ols import (
    ols_reports_from_scores,
    structural_paths_from_beta,
)
from sem_tool.validation.methodology import (
    merge_validation_warnings,
    parse_cb_factors_from_syntax_rows,
    read_hipotesis,
    read_indicadores_catalog,
    validate_cb_model,
    get_min_observations,
    validate_data_for_model,
)


@dataclass
class CbSemResult:
    fit_indices: pd.DataFrame
    paths_std: pd.DataFrame
    paths_raw: pd.DataFrame
    loadings: pd.DataFrame
    warnings: pd.DataFrame
    syntax: str
    decomposition: CovarianceDecomposition | None = None
    ols_sheets: dict[str, pd.DataFrame] | None = None
    error_sheets: dict[str, pd.DataFrame] | None = None
    parameters_sheet: pd.DataFrame | None = None
    identification_sheet: pd.DataFrame | None = None
    moment_system_sheets: dict[str, pd.DataFrame] | None = None
    fit_evaluation: pd.DataFrame | None = None
    fit_evaluation_modern: pd.DataFrame | None = None
    eqs_gof_report: pd.DataFrame | None = None


def run_cbsem(workbook_path: Path) -> CbSemResult:
    path = Path(workbook_path)
    data = xl.read_data(path)
    modelo = xl.read_sheet(path, SHEET_MODELO_CB)
    syntax = parse_modelo_cb(modelo)
    factors, struct_paths = parse_cb_factors_from_syntax_rows(modelo)
    catalog = read_indicadores_catalog(path)
    hipotesis = read_hipotesis(path)
    all_items = [it for items in factors.values() for it in items]

    min_obs = get_min_observations(path)
    method_report = validate_cb_model(factors, struct_paths, hipotesis)
    data_report = validate_data_for_model(
        data, all_items, catalog, min_obs_per_variable=min_obs
    )
    method_report.errors.extend(data_report.errors)
    method_report.warnings.extend(data_report.warnings)
    from sem_tool.spec.cb_syntax import check_identification_warnings

    for msg in check_identification_warnings(modelo):
        method_report.warnings.append({"tipo": "regla_6", "mensaje": msg})
    method_report.raise_if_errors()

    # Matriz S: covarianzas entre cada par de ítems (base del análisis factorial / EQS)
    desc = compute_descriptives(data, columns=all_items, min_obs_per_variable=min_obs)
    export_descriptives_to_workbook(path, desc)
    cov_matrix = desc.covarianza.loc[all_items, all_items]

    model = Model(syntax)
    complete_cases = data.dropna(subset=all_items)
    try:
        model.fit(cov=cov_matrix, n_samples=desc.n_casos)
    except Exception:
        model.fit(complete_cases[all_items])

    from sem_tool.cbsem.fit_criteria import collect_metrics_for_evaluation, evaluate_fit_indices
    from sem_tool.cbsem.fit_modern import (
        eqs_gof_summary_report,
        evaluate_fit_modern,
    )

    metrics, rmsr = collect_metrics_for_evaluation(model, cov_matrix)
    try:
        metrics["AIC"] = float(calc_aic(model, calc_likelihood(model)))
        metrics["BIC"] = float(calc_bic(model, calc_likelihood(model)))
        metrics["LogLik"] = float(calc_likelihood(model))
    except Exception:
        pass
    fit_df = append_fit_identification_rows(_metrics_to_fit_df(metrics), model)
    n_params = len(model.param_vals) if hasattr(model, "param_vals") else 0
    fit_evaluation = evaluate_fit_indices(metrics, desc.n_casos, n_params, rmsr=rmsr)
    fit_evaluation_modern = evaluate_fit_modern(metrics, desc.n_casos, n_params, rmsr=rmsr)
    eqs_gof_report = eqs_gof_summary_report(metrics, desc.n_casos, method="ML")
    identification_sheet = identification_report(model)
    mats = inspect_matrices(model)
    paths_raw = _beta_to_paths(mats.get("Beta"))
    loadings = _lambda_to_loadings(mats.get("Lambda"))
    paths_std = _standardize_paths(paths_raw, mats)
    decomp = decompose_covariance(model, cov_matrix)

    ols_sheets: dict[str, pd.DataFrame] = {}
    error_sheets = export_error_tables(model)
    parameters_sheet = parameters_report(model)
    try:
        scores = model.predict_factors(complete_cases[all_items])
        paths = structural_paths_from_beta(mats.get("Beta"))
        ols_min = min(min_obs, max(10, len(complete_cases)))
        reports = ols_reports_from_scores(scores, paths, min_n=ols_min)
        ols_sheets = reports_to_workbook_sheets(reports)
    except Exception:
        pass

    warnings = collect_warnings(data, n_params, len(syntax.splitlines()))
    id_warn = pd.DataFrame(identification_warnings(model))
    if not id_warn.empty:
        warnings = pd.concat([warnings, id_warn], ignore_index=True)
    warnings = merge_validation_warnings(warnings, method_report)

    moment_system_sheets = _build_moment_system_sheets(
        cov_matrix, factors, desc.n_casos, model
    )

    return CbSemResult(
        fit_indices=fit_df,
        fit_evaluation=fit_evaluation,
        fit_evaluation_modern=fit_evaluation_modern,
        eqs_gof_report=eqs_gof_report,
        paths_std=paths_std,
        paths_raw=paths_raw,
        loadings=loadings,
        warnings=warnings,
        syntax=syntax,
        decomposition=decomp,
        ols_sheets=ols_sheets or None,
        error_sheets=error_sheets or None,
        parameters_sheet=parameters_sheet,
        identification_sheet=identification_sheet,
        moment_system_sheets=moment_system_sheets,
    )


def _build_moment_system_sheets(
    cov_matrix: pd.DataFrame,
    factors: dict[str, list[str]],
    n_casos: int,
    model: Model,
) -> dict[str, pd.DataFrame] | None:
    """Sistema momento–parámetro del bloque CFA con más ítems (diapositiva F→V1…V4)."""
    block = _largest_factor_block(factors)
    if not block:
        return None
    factor_name, items = block
    items = [i for i in items if i in cov_matrix.index]
    if len(items) < 2:
        return None

    from sem_tool.cbsem.moment_equations import build_one_factor_system_report

    sheets = build_one_factor_system_report(
        cov_matrix, items, n_casos, factor_name=factor_name
    )
    if len(items) >= 2:
        sheets["Comparacion_semopy"] = _compare_closed_form_to_semopy(
            model, items[0], items[1], cov_matrix
        )
    return sheets


def _largest_factor_block(
    factors: dict[str, list[str]],
) -> tuple[str, list[str]] | None:
    best_name = ""
    best_items: list[str] = []
    for name, items in factors.items():
        if len(items) > len(best_items):
            best_name = name
            best_items = list(items)
    if len(best_items) < 2:
        return None
    return best_name, best_items


def _compare_closed_form_to_semopy(
    model: Model,
    item1: str,
    item2: str,
    cov: pd.DataFrame,
) -> pd.DataFrame:
    from semopy.inspector import inspect_list

    from sem_tool.cbsem.moment_equations import extract_moments_2_items

    v1, v2, c12 = extract_moments_2_items(cov, item1, item2)
    cerrado = {
        "λ₁": 1.0,
        "θ₁": v1 - 1.0,
        "λ₂": c12,
        "θ₂": v2 - c12**2,
    }
    semopy_vals: dict[str, float | None] = {k: None for k in cerrado}
    try:
        ins = inspect_list(model, information=None, std_est=False)
        for item, keys in ((item1, ("λ₁", "θ₁")), (item2, ("λ₂", "θ₂"))):
            lr = ins[(ins["lval"] == item) & (ins["op"] == "=~")]
            tr = ins[(ins["lval"] == item) & (ins["rval"] == item) & (ins["op"] == "~~")]
            if not lr.empty:
                semopy_vals[keys[0]] = float(lr["Estimate"].iloc[0])
            if not tr.empty:
                semopy_vals[keys[1]] = float(tr["Estimate"].iloc[0])
    except Exception:
        pass

    rows = []
    for param, cval in cerrado.items():
        sval = semopy_vals.get(param)
        fila = {
            "parametro": param,
            "solucion_cerrada_lambda1_1": cval,
            "semopy_estimado": sval,
            "teoria_igual_DATA": _check_moment_match(param, cval, v1, v2, c12),
        }
        if sval is not None and cval == cval:
            fila["diferencia_cerrado_semopy"] = abs(cval - sval)
        rows.append(fila)
    return pd.DataFrame(rows)


def _check_moment_match(param: str, val: float, v1: float, v2: float, c12: float) -> str:
    if param == "λ₁":
        return f"Var(1)={v1:.4f} debe ser λ₁²+θ₁"
    if param == "θ₁":
        return f"con λ₁=1 → θ₁={v1-1:.4f}"
    if param == "λ₂":
        return f"Cov={c12:.4f} debe ser λ₁λ₂"
    if param == "θ₂":
        return f"Var(2)={v2:.4f} debe ser λ₂²+θ₂"
    return ""


def export_cbsem(workbook_path: Path, result: CbSemResult) -> None:
    sheets = {
        "Fit_Indices": result.fit_indices,
    }
    if result.fit_evaluation is not None and not result.fit_evaluation.empty:
        sheets["Criterios_Ajuste"] = result.fit_evaluation
    if result.fit_evaluation_modern is not None and not result.fit_evaluation_modern.empty:
        sheets["Criterios_Ajuste_Modernos"] = result.fit_evaluation_modern
    if result.eqs_gof_report is not None and not result.eqs_gof_report.empty:
        sheets["Informe_Ajuste_EQS"] = result.eqs_gof_report
    sheets.update(
        {
            "Paths_Estandarizados": result.paths_std,
            "Paths_NoEstandarizados": result.paths_raw,
            "Loadings": result.loadings,
            "Warnings": result.warnings,
        }
    )
    if result.decomposition is not None:
        d = result.decomposition
        sheets.update(
            {
                "Matriz_Observada_DATA": d.observada,
                "Matriz_Implicita_MODEL": d.implicita,
                "Matriz_Residual": d.residual,
                "Residuales_Pares": d.residuales_pares,
                "Resumen_DATA_MODEL_RESIDUAL": d.resumen,
                "Ecuaciones_Structurales": d.ecuaciones,
                "Regresion_Structural": d.regresion_structural,
                "Hipotesis_Covarianzas": d.hipotesis_covarianzas,
                "Matriz_Sigma_Teoria": d.sigma_tesis,
                "Sigma_Teoria_Nota": d.sigma_tesis_nota,
            }
        )
        from sem_tool.cbsem.covariance_hypotheses import ejemplo_hipotesis_v1_v2

        sheets["Hipotesis_V1_V2"] = ejemplo_hipotesis_v1_v2()
    if result.moment_system_sheets:
        sheets.update(result.moment_system_sheets)
    if result.ols_sheets:
        sheets.update(result.ols_sheets)
    if result.error_sheets:
        sheets.update(result.error_sheets)
    if result.parameters_sheet is not None and not result.parameters_sheet.empty:
        sheets["Parametros_Modelo"] = result.parameters_sheet
    if result.identification_sheet is not None and not result.identification_sheet.empty:
        sheets["Identificacion_GL"] = result.identification_sheet
        from sem_tool.cbsem.identification import ejemplo_momentos_2x2

        sheets["Ejemplo_Matriz_2x2"] = ejemplo_momentos_2x2()
    from sem_tool.io.frederic_curriculum import identificacion_modelo_frederic, leyes_covarianzas_frederic

    sheets["Leyes_Covarianzas"] = leyes_covarianzas_frederic()
    sheets["Identificacion_Modelo"] = identificacion_modelo_frederic()
    xl.write_result_sheets(workbook_path, sheets)


def _metrics_to_fit_df(metrics: dict[str, float | None]) -> pd.DataFrame:
    rows = []
    for k, v in metrics.items():
        rows.append({"indice": k, "valor": float(v) if v is not None and v == v else None})
    return pd.DataFrame(rows)


def _compute_fit_indices(model: Model) -> pd.DataFrame:
    """Compat: índices vía fit_criteria.collect_metrics_for_evaluation."""
    from sem_tool.cbsem.fit_criteria import collect_metrics_for_evaluation

    metrics, _ = collect_metrics_for_evaluation(model, None)
    try:
        from semopy.stats import calc_aic, calc_bic, calc_likelihood

        metrics["AIC"] = float(calc_aic(model, calc_likelihood(model)))
        metrics["BIC"] = float(calc_bic(model, calc_likelihood(model)))
        metrics["LogLik"] = float(calc_likelihood(model))
    except Exception:
        pass
    return _metrics_to_fit_df(metrics)


def _beta_to_paths(beta: pd.DataFrame | None) -> pd.DataFrame:
    if beta is None or beta.empty:
        return pd.DataFrame(columns=["lhs", "rhs", "estimate"])
    rows = []
    for lhs in beta.index:
        for rhs in beta.columns:
            val = beta.loc[lhs, rhs]
            if val and abs(float(val)) > 1e-8:
                rows.append({"lhs": lhs, "rhs": rhs, "estimate": float(val)})
    return pd.DataFrame(rows)


def _lambda_to_loadings(lambda_mat: pd.DataFrame | None) -> pd.DataFrame:
    if lambda_mat is None or lambda_mat.empty:
        return pd.DataFrame(columns=["item", "factor", "loading"])
    rows = []
    for item in lambda_mat.index:
        for factor in lambda_mat.columns:
            val = lambda_mat.loc[item, factor]
            if val and abs(float(val)) > 1e-8:
                rows.append({"item": item, "factor": factor, "loading": float(val)})
    return pd.DataFrame(rows)


def _standardize_paths(
    paths: pd.DataFrame,
    mats: dict,
) -> pd.DataFrame:
    if paths.empty:
        return paths.copy()
    psi = mats.get("Psi")
    if psi is None:
        paths = paths.copy()
        paths["std_estimate"] = paths["estimate"]
        return paths
    out = paths.copy()
    std_vals = []
    for _, row in paths.iterrows():
        lhs, rhs = row["lhs"], row["rhs"]
        try:
            sd_lhs = float(psi.loc[lhs, lhs]) ** 0.5 if lhs in psi.index else 1.0
            sd_rhs = float(psi.loc[rhs, rhs]) ** 0.5 if rhs in psi.index else 1.0
            std_vals.append(row["estimate"] * sd_rhs / sd_lhs if sd_lhs else row["estimate"])
        except Exception:
            std_vals.append(row["estimate"])
    out["std_estimate"] = std_vals
    return out
