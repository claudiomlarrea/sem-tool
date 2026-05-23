"""Datos simulados Calidad → Satisfacción (taller Frederic / sem-tool)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sem_tool.io.schema import CB_COLUMNS


def likert_from_latent(
    rng: np.random.Generator,
    n: int,
    latent: np.ndarray,
    prefix: str,
    n_items: int = 3,
    n_categories: int = 5,
) -> pd.DataFrame:
    cols: dict[str, np.ndarray] = {}
    for i in range(1, n_items + 1):
        noise = rng.normal(scale=0.8, size=n)
        continuous = latent + noise
        ranks = pd.Series(continuous).rank(method="average").values
        cats = np.ceil(ranks / (n / n_categories)).astype(int)
        cols[f"{prefix}{i}"] = np.clip(cats, 1, n_categories)
    return pd.DataFrame(cols)


def frederic_datos(n: int = 200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    calidad = rng.normal(size=n)
    satisfaccion = 0.55 * calidad + rng.normal(scale=0.6, size=n)
    datos = likert_from_latent(rng, n, calidad, "CAL", n_items=3)
    datos = datos.join(likert_from_latent(rng, n, satisfaccion, "SAT", n_items=3))
    return datos


def frederic_modelo_cb() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["medicion", "Calidad", "MEAS", "CAL1 + CAL2 + CAL3", "", "1"],
            ["medicion", "Satisfaccion", "MEAS", "SAT1 + SAT2 + SAT3", "", "1"],
            ["estructural", "Satisfaccion", "REG", "Calidad", "", ""],
        ],
        columns=list(CB_COLUMNS),
    )


def frederic_modelo_pls() -> pd.DataFrame:
    rows = []
    for construct, prefix in [("Calidad", "CAL"), ("Satisfaccion", "SAT")]:
        for j in range(1, 4):
            rows.append([construct, f"{prefix}{j}", "A", "", "", "ítem reflexivo"])
    rows.append(["Calidad", "", "A", "Calidad", "Satisfaccion", "H1 estructural"])
    return pd.DataFrame(
        rows,
        columns=["constructo", "indicador", "modo", "ruta_origen", "ruta_destino", "notas"],
    )


def restaurant_datos(n: int = 20, seed: int = 2024) -> pd.DataFrame:
    """20 clientes — calidad percibida → satisfacción (restaurante, Likert 1–5)."""
    rng = np.random.default_rng(seed)
    calidad = rng.normal(loc=0.3, scale=1.0, size=n)
    satisfaccion = 0.6 * calidad + rng.normal(scale=0.55, size=n)
    frame = likert_from_latent(rng, n, calidad, "CAL", n_items=3, n_categories=5)
    frame = frame.join(
        likert_from_latent(rng, n, satisfaccion, "SAT", n_items=3, n_categories=5)
    )
    frame.insert(0, "cliente_id", np.arange(1, n + 1))
    return frame


def restaurant_indicadores() -> pd.DataFrame:
    rows = [
        {
            "constructo": "Calidad",
            "indicador": "CAL1",
            "escala": "Likert",
            "puntos": 5,
            "referencia": "Adaptado SERVQUAL — dimensión tangibles/alimentos",
            "notas": "La comida del restaurante es de buena calidad",
        },
        {
            "constructo": "Calidad",
            "indicador": "CAL2",
            "escala": "Likert",
            "puntos": 5,
            "referencia": "Adaptado SERVQUAL — dimensión servicio",
            "notas": "El personal es amable y atento",
        },
        {
            "constructo": "Calidad",
            "indicador": "CAL3",
            "escala": "Likert",
            "puntos": 5,
            "referencia": "Adaptado SERVQUAL — ambiente",
            "notas": "El local está limpio y es agradable",
        },
        {
            "constructo": "Satisfaccion",
            "indicador": "SAT1",
            "escala": "Likert",
            "puntos": 5,
            "referencia": "Satisfacción global — literatura hospitalidad",
            "notas": "En general estoy satisfecho con mi experiencia en el restaurante",
        },
        {
            "constructo": "Satisfaccion",
            "indicador": "SAT2",
            "escala": "Likert",
            "puntos": 5,
            "referencia": "Intención de recomendación (NPS / lealtad)",
            "notas": "Recomendaría este restaurante a familiares o amigos",
        },
        {
            "constructo": "Satisfaccion",
            "indicador": "SAT3",
            "escala": "Likert",
            "puntos": 5,
            "referencia": "Intención de repurchase",
            "notas": "Volvería a visitar este restaurante",
        },
    ]
    return pd.DataFrame(rows)


def restaurant_hipotesis() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "origen": "Calidad",
                "destino": "Satisfaccion",
                "hipotesis": (
                    "H1: La calidad percibida del restaurante "
                    "impacta positivamente la satisfacción del cliente"
                ),
                "referencia": "Parasuraman et al. (1988); Oliver (1997) — adaptar cita",
                "argumento": (
                    "Mayor calidad en comida, servicio y ambiente se asocia "
                    "con mayor satisfacción y lealtad en restauración."
                ),
            }
        ]
    )


def frederic_indicadores() -> pd.DataFrame:
    rows = []
    for construct, prefix, ref in [
        ("Calidad", "CAL", "SERVQUAL / calidad de servicio"),
        ("Satisfaccion", "SAT", "Escala de satisfacción"),
    ]:
        for n in range(1, 4):
            rows.append(
                {
                    "constructo": construct,
                    "indicador": f"{prefix}{n}",
                    "escala": "Likert",
                    "puntos": 5,
                    "referencia": ref,
                    "notas": "Mínimo 3 ítems por constructo (validación sem-tool)",
                }
            )
    return pd.DataFrame(rows)
