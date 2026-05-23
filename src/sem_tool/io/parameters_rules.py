"""Reglas para determinar parámetros del modelo (diapositiva SEM)."""

from __future__ import annotations

import pandas as pd

SHEET_REGLAS_PARAMETROS = "Reglas_Parametros"


def reglas_parametros_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "regla": 1,
                "tipo": "Sí es parámetro",
                "descripcion": "Todas las varianzas de las variables independientes",
                "en_sem_tool": "Varianzas de factores exógenos (Psi) estimadas o fijadas",
            },
            {
                "regla": 2,
                "tipo": "Sí es parámetro",
                "descripcion": "Todas las covarianzas entre variables independientes",
                "en_sem_tool": "Filas COV en Modelo_CB (~~ entre exógenos)",
            },
            {
                "regla": 3,
                "tipo": "Sí es parámetro",
                "descripcion": "Todas las cargas factoriales (latente → indicadores)",
                "en_sem_tool": "Filas MEAS (=~) en Modelo_CB; loadings en Loadings",
            },
            {
                "regla": 4,
                "tipo": "Sí es parámetro",
                "descripcion": "Todos los coeficientes de regresión (observadas o latentes)",
                "en_sem_tool": "Filas REG (~) ej. Satisfaccion ~ Calidad → pendiente b",
            },
            {
                "regla": 5,
                "tipo": "Nunca es parámetro",
                "descripcion": "(i) Varianzas de dependientes; (ii) covarianzas entre dependientes; "
                "(iii) covarianzas entre dependiente e independiente",
                "en_sem_tool": "Se calculan a partir de otros parámetros (modelo implícito)",
            },
            {
                "regla": 6,
                "tipo": "Fijar métrica del latente",
                "descripcion": "Exógeno: varianza=1 o carga fija a 1. Endógeno: coeficiente fijo a 1",
                "en_sem_tool": "Columna fixed=1 en MEAS (carga 1*ítem) o varianza fijada en semopy",
            },
        ]
    )


def identificacion_checklist() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "paso": [
                "Exógenos (F1 Calidad)",
                "Endógenos (F2 Satisfacción)",
                "Cargas (=~)",
                "Rutas (~)",
                "Covarianzas exógenas (~~)",
            ],
            "regla_aplicada": [
                "Regla 6: fijar 1*primer ítem o varianza",
                "Regla 5: varianza residual D (Psi) derivada",
                "Regla 3: parámetros libres salvo 1 fijado",
                "Regla 4: pendiente b estimada",
                "Regla 2: opcional COV entre exógenos",
            ],
            "en_Modelo_CB": [
                "MEAS Calidad + fixed=1 en primer ítem",
                "REG Satisfaccion ~ Calidad",
                "CAL1 + CAL2 + CAL3",
                "Satisfaccion REG Calidad",
                "solo si hay 2+ exógenos",
            ],
        }
    )


def slide_cfa_4_items_template() -> pd.DataFrame:
    from sem_tool.cbsem.moment_equations import slide_cfa_4_items_template as _t

    return _t()


def sistema_3_ecuaciones_template() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "paso": [
                "1. DATA (500 casos)",
                "2. Tres números",
                "3. Tres ecuaciones",
                "4. Cuatro incógnitas",
                "5. Fijar λ₁=1",
                "6. Teoría = práctica",
            ],
            "detalle": [
                "Calcular S: Var(1), Var(2), Cov(1,2) en Matriz_Covarianzas",
                "p×(p+1)/2 = 2×3/2 = 3 momentos",
                "Var(1)=λ₁²+θ₁; Var(2)=λ₂²+θ₂; Cov(1,2)=λ₁λ₂",
                "λ₁, λ₂, θ₁, θ₂ → 3 ecuaciones, 4 parámetros → subidentificado",
                "Regla 6: una restricción → 3 ecuaciones, 3 desconocidos",
                "Σ estimada debe igualar los 3 valores de S (ver Matriz_Residual)",
            ],
        }
    )


def ejemplo_hipotesis_v1_v2_template() -> pd.DataFrame:
    from sem_tool.cbsem.covariance_hypotheses import ejemplo_hipotesis_v1_v2

    return ejemplo_hipotesis_v1_v2()


def ejemplo_matriz_2x2_template() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "simbolo": ["V1", "V2", "V1↔V2", "V1↔V2"],
            "celda_S": ["S(V1,V1)", "S(V2,V2)", "S(V1,V2)", "S(V2,V1)"],
            "tipo_dato": [
                "Varianza de V1 (no confundir: V1 es el ítem, no ‘varianza’)",
                "Varianza de V2",
                "Covarianza V1 con V2",
                "Igual que la anterior (matriz simétrica)",
            ],
            "cuenta_momentos": ["1/3", "2/3", "3/3", "(misma que 3/3)"],
            "en_estudio_completo": ["CAL1", "CAL2", "Cov(CAL1,CAL2)", "mismo valor"],
        }
    )


def grados_libertad_explicacion() -> pd.DataFrame:
    """Tabla didáctica: momentos S vs GL (p×(p+1)/2 − t)."""
    return pd.DataFrame(
        [
            {
                "concepto": "Ejemplo 2×2 (V1 y V2)",
                "detalle": "V1,V2 = ítems observados. 3 datos: Var(V1), Var(V2), Cov(V1,V2)=Cov(V2,V1)",
                "formula": "p×(p+1)/2 = 2×(2+1)/2 = 2×3/2 = 3",
            },
            {
                "concepto": "Matriz S (DATA)",
                "detalle": "Matriz simétrica p×p: diagonal (varianzas) + covarianzas únicas",
                "formula": "Nº de datos = p×(p+1)/2  (no p×p; la mitad superior basta)",
            },
            {
                "concepto": "Covarianzas únicas",
                "detalle": "Fuera de la diagonal (p=2 → solo cov₁₂)",
                "formula": "p×(p−1)/2 (p=2 → 1; p=5 → 10)",
            },
            {
                "concepto": "Ejemplo 5 ítems (p=5)",
                "detalle": "15 datos: 5 varianzas + 10 covarianzas",
                "formula": "5×(5+1)/2 = 5×6/2 = 15",
            },
            {
                "concepto": "Parámetros libres (t)",
                "detalle": "Cargas, regresiones, varianzas exógenas (reglas 1–4, 6)",
                "formula": "Contados por sem-tool en Parametros_Modelo",
            },
            {
                "concepto": "Grados de libertad (GL)",
                "detalle": "Deben ser > 0; si son demasiados, el modelo no ‘cuadra’ con S",
                "formula": "GL = p×(p+1)/2 − t  (mismo DoF que EQS/semopy)",
            },
            {
                "concepto": "Equilibrio",
                "detalle": "GL positivo pero no casi igual a todos los momentos",
                "formula": "Advertencia si GL/momentos > 75%",
            },
        ]
    )
