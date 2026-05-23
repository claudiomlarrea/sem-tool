"""
sem-tool — interfaz web (Streamlit).

Ejecutar en local:
    pip install -e ".[web]"
    streamlit run streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from sem_tool.web.pipeline import (
    cleanup_workdir,
    copy_upload_to_workdir,
    create_template_bytes,
    read_sheet_preview,
    run_pipeline,
    workbook_sheet_names,
)

st.set_page_config(
    page_title="sem-tool · UCCuyo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Colores UCCuyo (Manual identidad visual v1.0 — extraídos del PDF institucional)
UCC_VERDE = "#009640"
UCC_AZUL = "#312783"
UCC_GRIS_60 = "#878787"
UCC_NEGRO = "#1D1D1B"
UCC_FONDO = "#F6F6F6"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {UCC_AZUL} 0%, #252060 100%);
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stMarkdown strong {{
        color: #ffffff !important;
    }}
    div[data-testid="stSidebarNav"] {{
        background-color: transparent;
    }}
    .ucc-header {{
        border-left: 5px solid {UCC_VERDE};
        padding-left: 0.75rem;
        margin-bottom: 0.25rem;
    }}
    .ucc-header h1 {{
        color: {UCC_AZUL};
        font-weight: 700;
        margin: 0;
        font-size: 1.75rem;
    }}
    .ucc-header p {{
        color: {UCC_GRIS_60};
        margin: 0;
        font-size: 0.95rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

PREVIEW_SHEETS_CB = [
    "Fit_Indices",
    "Criterios_Ajuste",
    "Paths_Estandarizados",
    "Loadings",
    "Warnings",
]
PREVIEW_SHEETS_PLS = [
    "Outer_Loadings",
    "Paths",
    "AVE_CR",
    "HTMT",
    "Bootstraps",
    "R2",
]


def _sidebar() -> None:
    st.sidebar.markdown("### sem-tool")
    st.sidebar.caption("CB-SEM (EQS) · PLS-SEM (SmartPLS)")
    st.sidebar.markdown(
        """
        **Flujo**
        1. Descargar plantilla o subir su `.xlsx`
        2. Rellenar hoja `Datos` y modelos
        3. Ejecutar análisis
        4. Descargar Excel con resultados
        """
    )


def _tab_plantilla() -> None:
    st.header("Plantilla Excel")
    col1, col2, col3 = st.columns(3)
    with col1:
        perfil = st.selectbox(
            "Perfil",
            ["frederic", "restaurante"],
            format_func=lambda p: {
                "frederic": "Taller UIC (Calidad → Satisfacción)",
                "restaurante": "Restaurante (20 clientes)",
            }[p],
        )
    with col2:
        mode = st.selectbox("Modo", ["both", "cb", "pls"], format_func=lambda m: {
            "both": "CB + PLS",
            "cb": "Solo CB-SEM",
            "pls": "Solo PLS-SEM",
        }[m])
    with col3:
        sample = st.radio(
            "Datos",
            [True, False],
            format_func=lambda x: (
                "Con datos de ejemplo" if x else "Vacía (solo encabezados)"
            ),
            horizontal=True,
        )

    if st.button("Generar plantilla", type="primary"):
        data = create_template_bytes(
            mode=mode,  # type: ignore[arg-type]
            include_sample=sample,
            profile=perfil,
            n_respondents=20,
        )
        st.session_state["template_bytes"] = data
        name = (
            "encuesta_restaurante_20.xlsx"
            if perfil == "restaurante" and sample
            else f"plantilla_{perfil}_{mode}.xlsx"
        )
        st.session_state["template_name"] = name
        st.success("Plantilla lista para descargar.")

    if "template_bytes" in st.session_state:
        st.download_button(
            "⬇️ Descargar .xlsx",
            data=st.session_state["template_bytes"],
            file_name=st.session_state.get("template_name", "plantilla_sem.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _tab_analizar() -> None:
    st.header("Analizar libro Excel")
    uploaded = st.file_uploader(
        "Subir archivo .xlsx",
        type=["xlsx"],
        help="Debe incluir hoja Datos y Modelo_CB y/o Modelo_PLS",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        run_desc = st.checkbox("Descriptivos", value=True)
        run_cb = st.checkbox("CB-SEM (EQS)", value=True)
        run_pls = st.checkbox("PLS-SEM (SmartPLS)", value=True)
    with col_b:
        bootstraps = st.number_input(
            "Bootstrap PLS",
            min_value=100,
            max_value=10000,
            value=500,
            step=100,
        )
        processes = st.number_input("Procesos PLS", min_value=1, max_value=8, value=2)

    if uploaded is None:
        st.info("Suba un Excel o genere una plantilla en la pestaña anterior.")
        return

    if st.button("Ejecutar análisis", type="primary"):
        work_path: Path | None = st.session_state.get("work_path")
        if work_path and work_path.exists():
            cleanup_workdir(work_path)
        work_path = copy_upload_to_workdir(uploaded.getvalue(), uploaded.name)
        st.session_state["work_path"] = work_path

        with st.spinner("Calculando SEM… (PLS con bootstrap puede tardar unos minutos)"):
            try:
                result = run_pipeline(
                    work_path,
                    descriptivos=run_desc,
                    cb=run_cb,
                    pls=run_pls,
                    bootstraps=int(bootstraps),
                    processes=int(processes),
                )
                st.session_state["result_bytes"] = work_path.read_bytes()
                st.session_state["result_name"] = Path(uploaded.name).stem + "_resultados.xlsx"
                st.session_state["pipeline_logs"] = result.logs
                st.session_state["sheet_names"] = sorted(workbook_sheet_names(work_path))
            except Exception as exc:
                st.error(f"Error en el análisis:\n\n{exc}")
                return

        st.success("Análisis completado.")

    if "pipeline_logs" in st.session_state:
        for log in st.session_state["pipeline_logs"]:
            if log.level == "warning":
                st.warning(f"**{log.step}**: {log.message}")
            else:
                st.write(f"✓ **{log.step}**: {log.message}")

    if "result_bytes" in st.session_state:
        st.download_button(
            "⬇️ Descargar Excel con resultados",
            data=st.session_state["result_bytes"],
            file_name=st.session_state.get("result_name", "resultados.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )


def _tab_vista_previa() -> None:
    st.header("Vista previa de hojas")
    if "work_path" not in st.session_state or not st.session_state["work_path"].exists():
        st.info("Ejecute primero un análisis en la pestaña «Analizar».")
        return

    path: Path = st.session_state["work_path"]
    names = sorted(workbook_sheet_names(path))
    preferred = [s for s in PREVIEW_SHEETS_CB + PREVIEW_SHEETS_PLS if s in names]
    options = preferred + [s for s in names if s not in preferred]
    sheet = st.selectbox("Hoja", options, index=0)

    try:
        df = read_sheet_preview(path, sheet, max_rows=40)
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as exc:
        st.warning(str(exc))


def _tab_ayuda() -> None:
    st.header("Ayuda")
    st.markdown(
        """
        ### Uso local
        ```bash
        python3 -m pip install -e ".[web]"
        streamlit run streamlit_app.py
        ```

        ### CLI (sin web)
        ```bash
        python3 -m sem_tool init -o estudio.xlsx
        python3 -m sem_tool run-all estudio.xlsx --bootstraps 500 --processes 2
        ```

        ### Ejemplo restaurante (20 clientes)
        ```bash
        python3 -m sem_tool ejemplo-restaurante -o encuesta_restaurante_20.xlsx
        ```
        """
    )


def main() -> None:
    _sidebar()
    st.markdown(
        """
        <div class="ucc-header">
            <h1>sem-tool</h1>
            <p>Ecuaciones estructurales · CB-SEM y PLS-SEM · UCCuyo</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Plantilla", "Analizar", "Vista previa", "Ayuda"]
    )
    with tab1:
        _tab_plantilla()
    with tab2:
        _tab_analizar()
    with tab3:
        _tab_vista_previa()
    with tab4:
        _tab_ayuda()


if __name__ == "__main__":
    main()
