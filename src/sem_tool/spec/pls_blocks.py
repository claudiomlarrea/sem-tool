"""Convert Modelo_PLS sheet to plspm Config."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
from plspm.config import Config, MV, Structure
from plspm.mode import Mode

from sem_tool.io.schema import (
    PLS_INDICATOR_COLUMNS,
    PLS_PATH_COLUMNS,
    SHEET_MODELO_PLS,
    validate_columns,
)


@dataclass
class PlsModelSpec:
    config: Config
    constructs: list[str] = field(default_factory=list)


def parse_modelo_pls(df: pd.DataFrame) -> PlsModelSpec:
    col_map = {str(c).lower(): c for c in df.columns}
    missing = [c for c in ("constructo", "indicador", "modo") if c not in col_map]
    if missing:
        raise ValueError(
            f"Hoja '{SHEET_MODELO_PLS}': faltan columnas {missing}. "
            f"Encontradas: {list(df.columns)}"
        )

    construct_col = col_map.get("constructo", "constructo")
    indicator_col = col_map.get("indicador", "indicador")
    mode_col = col_map.get("modo", "modo")
    origin_col = col_map.get("ruta_origen", "ruta_origen")
    dest_col = col_map.get("ruta_destino", "ruta_destino")

    blocks: dict[str, list[tuple[str, Mode]]] = {}
    paths: list[tuple[str, str]] = []

    for _, row in df.iterrows():
        lv = _str(row.get(construct_col))
        mv = _str(row.get(indicator_col))
        modo = _str(row.get(mode_col)).upper()
        origin = _str(row.get(origin_col))
        dest = _str(row.get(dest_col))

        if lv and mv:
            mode = Mode.B if modo == "B" else Mode.A
            blocks.setdefault(lv, []).append((mv, mode))

        if origin and dest and origin != dest:
            paths.append((origin, dest))

    if not blocks:
        raise ValueError("Modelo_PLS: defina al menos un constructo con indicadores.")

    structure = Structure()
    seen_paths: set[tuple[str, str]] = set()
    for origin, dest in paths:
        key = (origin, dest)
        if key not in seen_paths:
            structure.add_path([origin], [dest])
            seen_paths.add(key)

    import numpy as np

    if paths:
        path_matrix = structure.path()
    else:
        path_matrix = pd.DataFrame()

    index = list(blocks.keys())
    if path_matrix.empty or set(path_matrix.index) != set(index):
        path_matrix = pd.DataFrame(
            np.zeros((len(index), len(index)), dtype=int),
            columns=index,
            index=index,
        )
    else:
        # ensure all constructs appear
        for lv in index:
            if lv not in path_matrix.index:
                raise ValueError(f"Constructo '{lv}' no está en la estructura de rutas.")

    config = Config(path_matrix)
    constructs: list[str] = []
    for lv, indicators in blocks.items():
        mvs = [MV(name=mv) for mv, _ in indicators]
        mode = indicators[0][1]
        config.add_lv(lv, mode, *mvs)
        constructs.append(lv)

    return PlsModelSpec(config=config, constructs=constructs)


def _str(val) -> str:
    if pd.isna(val):
        return ""
    return str(val).strip()
