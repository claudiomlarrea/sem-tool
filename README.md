# sem-tool

Programa en Python para **ecuaciones estructurales** con flujo de trabajo en **Excel**, alineado al taller **Frederic Marimon / Marta Mas (UIC)** — *Structural Equation Modeling (SEM)* — y a dos enfoques habituales:

| Software | Enfoque | Módulo sem-tool |
|----------|---------|-----------------|
| **EQS** | CB-SEM (covarianzas, ML, índices de ajuste global) | `sem-tool cb` |
| **SmartPLS** | PLS-SEM (varianza, bootstrapping, AVE/HTMT) | `sem-tool pls` |

## Curso Frederic (PPT → hojas Excel)

El contenido del PowerPoint del curso se refleja en plantillas y resultados:

| Hoja | Contenido del PPT |
|------|-------------------|
| **Curso_Frederic_SEM** | Índice del taller y enlace a hojas sem-tool |
| **Leyes_Covarianzas** | Leyes 1–4 (Cov(X,X)=Var(X), etc.) |
| **Identificacion_Modelo** | Sub / just / sobreidentificado |
| **Modelo_UIC_F1_F2** | F1 Calidad → F2 Satisfacción, GL=4 con 5 ítems |
| **Logica_Chi_Cuadrado** | S vs Σ, H₀/H₁, N≥10×t |
| **EQS_vs_SmartPLS** | Salidas EQS vs SmartPLS vs sem-tool |

Texto extraído del `.pptx`: [`docs/frederic_sem_ppt_extract.txt`](docs/frederic_sem_ppt_extract.txt). Para regenerar:

```bash
pip install python-pptx
python scripts/extract_frederic_ppt.py
```

## Instalación

En macOS suele existir `python3` pero **no** el comando `pip` ni `sem-tool` en el PATH hasta configurarlos.

```bash
cd /Users/claudiolarrea/Projects/sem-tool
python3 -m pip install -e ".[dev]"
```

Si tras instalar aparece *"script sem-tool is installed in .../Python/3.9/bin which is not on PATH"*, elige **una** opción:

**A) Añadir al PATH** (recomendado; pegar en `~/.zshrc` y luego `source ~/.zshrc`):

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
```

**B) Sin tocar PATH** — usar el módulo Python:

```bash
python3 -m sem_tool init --mode both -o taller_frederic.xlsx
python3 -m sem_tool descriptivos taller_frederic.xlsx
python3 -m sem_tool cb taller_frederic.xlsx
python3 -m sem_tool pls taller_frederic.xlsx --bootstraps 5000 --processes 2
```

Comprobar: `sem-tool --help` o `python3 -m sem_tool --help`.

Requisitos: Python 3.9+, dependencias `semopy`, `plspm`, `pandas`, `openpyxl`, `typer`.

## Uso rápido

```bash
# Plantillas vacías
sem-tool init --mode cb -o mi_cb.xlsx
sem-tool init --mode pls -o mi_pls.xlsx
sem-tool init --mode both -o mi_estudio.xlsx

# Paso previo: medias, varianzas y matriz de covarianzas
sem-tool descriptivos mi_estudio.xlsx

# Análisis SEM (también recalcula descriptivos al inicio)
sem-tool cb mi_estudio.xlsx
sem-tool pls mi_estudio.xlsx --bootstraps 5000 --processes 2
sem-tool run-all mi_estudio.xlsx
```

### Hojas de descriptivos (después de `descriptivos` o `cb`/`pls`)

| Hoja | Contenido |
|------|-----------|
| **Descriptivos** | Media, varianza y desviación por ítem |
| **Matriz_Covarianzas** | Matriz **S**: covarianza entre **cada par** de variables observadas |
| **Covarianzas_Pares** | Misma información en formato largo (`variable_1`, `variable_2`, `covarianza`) |
| **Matriz_Correlaciones** | Matriz R (equivalente normalizada) |
| **Medias** | Vector de medias |
| **Info_Descriptivos** | N de casos y nota de uso |

**Análisis factorial / CB-SEM (EQS):** el modelo no ajusta filas una por una, sino que reproduce la **matriz de covarianzas** entre ítems. Tras estimar:

| Concepto | Hoja Excel | Significado |
|----------|------------|-------------|
| **DATA** | `Matriz_Covarianzas` / `Matriz_Observada_DATA` | Covarianzas observadas (S) |
| **MODEL** | `Matriz_Implicita_MODEL` | Covarianzas que impone el modelo (Σ) |
| **RESIDUAL** | `Matriz_Residual` | S − Σ (lo no explicado) |

**Ecuación:** DATA = MODEL + RESIDUAL.

**Ecuaciones estructurales** (ej. satisfacción): hoja `Ecuaciones_Structurales` en forma **Y = a + b·X** (p. ej. `Satisfaccion = a + b*Calidad`) más las ecuaciones de medida ítem = λ·factor.

**Tu dibujo / tesis — matriz Σ (arriba, teoría):**

| Celda Σ | Fórmula en el dibujo (Var del factor = 1) |
|---------|-------------------------------------------|
| Var del ítem 1 (línea central / diagonal) | **λ₁² + σ₁** |
| Cov(1, 2) | **λ₁ × λ₂** |
| Var del ítem 2 | **λ₂² + σ₂** |

- **σ** (en el dibujo) = varianza del **error de medida** del ítem.  
- **Σ** (sigma griega) = matriz teórica → hoja **`Matriz_Sigma_Teoria`**.  
- **S** (datos) = **`Matriz_Covarianzas`**.  
- Estimación con semopy (ψ libre): **λ²ψ + θ** y **λ₁λ₂ψ** → **`Matriz_Implicita_MODEL`**.

Hoja **`Hipotesis_Covarianzas`**: columnas `formula_tesis`, `formula_estimacion`, `valor_Sigma_tesis`, `valor_Sigma_modelo`, `valor_DATA`.

### Un factor F con 4 ítems (diapositiva V1–V4, E1–E4)

Diagrama: **F → V1…V4**, errores **θ₁…θ₄**, **Var(F)=1**.

| | Cálculo |
|---|---------|
| **Ecuaciones** | 10 = (4)(5)/2 momentos en S |
| **Incógnitas** | 8 = λ₁…λ₄ + θ₁…θ₄ |
| **Grados de libertad** | 10 − 8 = **2 > 0** → **sobreidentificado** (permite contrastar el modelo) |

- **Varianzas:** λ₁²+θ₁=Var(V1), …, λ₄²+θ₄=Var(V4)  
- **Covarianzas:** λ₁λ₂=Cov(V1,V2), λ₁λ₃=…, λ₃λ₄=Cov(V3,V4), etc.

Hojas: **`Sistema_10_Ecuaciones`**, **`Identificacion_4_Items_1_Factor`**, **`Ecuaciones_Varianzas`**, **`Ecuaciones_Covarianzas`** (con los valores de tu muestra en el bloque CFA con más ítems, p. ej. CAL1–CAL4).

### Caso 500 observaciones, 2 ítems: 3 ecuaciones y 4 incógnitas

Con **Var(1)**, **Var(2)** y **Cov(1,2)** de tu muestra (hoja `Matriz_Covarianzas`):

| Ecuación | DATA (práctica) | = Teoría |
|----------|-----------------|----------|
| 1 | Var(1) del caso | λ₁² + θ₁ |
| 2 | Var(2) | λ₂² + θ₂ |
| 3 | Cov(1,2) | λ₁ × λ₂ |

**Incógnitas:** λ₁, λ₂, θ₁, θ₂ → **4 parámetros**, **3 ecuaciones** → hace falta **fijar uno** (p. ej. **λ₁ = 1**). Tras `sem-tool cb`: hojas **`Sistema_3_Ecuaciones`**, **`Identificacion_2_Items`**, **`Solucion_lambda1_igual_1`** (con tus números reales del primer par de ítems del factor).

### Regresión estructural (pendiente y R²)

El modelo realiza el equivalente a una **regresión** entre constructos. Lo central es la **pendiente b** (efecto de Calidad sobre Satisfacción):

| Hoja | Contenido |
|------|-----------|
| **Regresion_Structural** | `pendiente_b`, `pendiente_estandarizada`, **R²**, ecuación Y = a + b·X |
| **R2** (PLS) | Varianza explicada de cada constructo endógeno |
| **Bootstraps** (PLS) | Significancia de la pendiente / ruta |

Ejemplo CB: `Satisfaccion = 0 + b*Calidad` con **R²** = proporción de varianza de Satisfacción explicada por Calidad.

### Análisis de la varianza de la regresión (formato Excel / diapositiva)

Sobre las puntuaciones de los constructos, el programa genera las mismas tablas que Excel:

| Hoja | Contenido |
|------|-----------|
| **Regresion_Estadisticos** | R múltiple, **R²**, R² ajustado, error típico, n |
| **Regresion_ANOVA** | Regresión / Residuos / Total (gl, suma de cuadrados, F, p) |
| **Regresion_Coeficientes** | **Intercepción (a)**, **pendiente (b)**, error típico, **t**, **Probabilidad**, IC 95 % |

La **pendiente** de `Variable X 1` es el efecto de Calidad sobre Satisfacción; el **R²** indica cuánta varianza de Y explica X.

### Reglas para parámetros del modelo (identificación)

Hojas **Reglas_Parametros** y **Checklist_Identificacion** (6 reglas de la diapositiva):

| Regla | Contenido |
|-------|-----------|
| 1–2 | Varianzas y covarianzas de **independientes** → parámetros |
| 3 | **Cargas** latente–ítem (=~) → parámetros |
| 4 | **Regresiones** (~) → parámetros (pendiente b) |
| 5 | Varianzas/cov. de **dependientes** → no libres (derivadas) |
| 6 | **Métrica** del latente: `fixed=1` en un MEAS (carga 1*ítem) |

Tras `sem-tool cb`: hoja **Parametros_Modelo** lista cada parámetro estimado y la regla SEM aplicable.

### Grados de libertad (equilibrio con la matriz S)

La matriz de covarianzas observada **S** (p×p, simétrica) tiene **p×(p+1)/2** datos únicos — no p×p celdas, porque la matriz es simétrica.

**Ejemplo 2×2 (p = 2 ítems, p. ej. V1 y V2 del diagrama):** solo hay **3** datos en **S**:

| Símbolo | En la matriz S | Tipo |
|---------|----------------|------|
| **V1** | S(V1,V1) | **Varianza de** V1 (V1 es el ítem, no significa “varianza”) |
| **V2** | S(V2,V2) | **Varianza de** V2 |
| **V1 y V2** | S(V1,V2) = S(V2,V1) | **Covarianza** entre V1 y V2 (mismo número en ambas celdas) |

En el estudio completo: V1→CAL1, V2→CAL2 (hoja **Diagrama_SEM**).

Fórmula: **p×(p+1)/2 = 2×(2+1)/2 = 2×3/2 = 3**.

**Ejemplo con 5 ítems (p = 5):** **5×6/2 = 15** momentos (5 varianzas + 10 covarianzas = **5×4/2**).

| Cantidad | Fórmula |
|----------|---------|
| Momentos en S | p×(p+1)/2 |
| Covarianzas únicas | p×(p−1)/2 |
| Parámetros libres | t (estimados) |
| **Grados de libertad** | **GL = p×(p+1)/2 − t** |

- **GL &lt; 0**: subidentificado (demasiados parámetros).
- **GL = 0**: identificación exacta (frágil).
- **GL &gt; 0**: sobreidentificado (lo habitual).
- **GL demasiado alto** (p. ej. &gt; 75% de los momentos): pocos parámetros; el modelo no explica bien las covarianzas.

Hojas: **Grados_Libertad** (plantilla), **Identificacion_GL** (resultado tras `sem-tool cb`), índices `momentos_S` y `DoF_verificacion` en **Fit_Indices**.

### Diagrama de la diapositiva (F1 → F2)

Hojas **Diagrama_SEM** y **Resumen_Diagrama**:

```
F1 (Calidad)  ←── V1, V2, V3  (+ E1, E2, E3)
       │
       ▼
F2 (Satisfacción) ←── V4, V5  (+ E4, E5, D2)
```

- **Hipótesis:** la satisfacción (F2) está relacionada con la calidad (F1).
- **DATA:** ítems en `Datos` (covarianzas → análisis factorial / SEM).
- **MODEL + RESIDUAL:** `Matriz_Implicita_MODEL` + `Matriz_Residual`.
- **Errores_Medicion** / **Errores_Estructurales:** E en ítems, **D2** en Satisfacción.

En aula la diapositiva usa 2 ítems de satisfacción; el programa pide **≥3 por constructo** (añada SAT3).

### Tipos de variables (diagrama SEM)

Hoja **Tipos_Variables** (como en la diapositiva):

| Símbolo | Significado | En sem-tool |
|---------|-------------|-------------|
| **V** | Variable observada (ítem) | Columnas en `Datos` |
| **F** | Factor latente | `Calidad`, `Satisfaccion` en el modelo |
| **E** | Error de medida | Error ítem–factor (CFA) |
| **D** | Perturbación / residual del factor | Parte no explicada del endógeno |
| **F1↔F2** | Covarianza entre factores | Opcional: tipo COV en `Modelo_CB` |

### Significancia de la pendiente (t > 1,96)

En **Regresion_Coeficientes**, columna **robusto_alpha_005**: **Sí** si |t| > 1,96 (coeficientes robustos al 5 %, como en la diapositiva). La fila **pendiente b** es la hipótesis H1 (efecto de Calidad sobre Satisfacción).

Covarianza entre dos variables X e Y: \(\mathrm{Cov}(X,Y)=\frac{1}{n-1}\sum(x_i-\bar{x})(y_i-\bar{y})\). En la diagonal de **Matriz_Covarianzas** aparece la **varianza** de cada ítem.

Varianza y covarianzas son **muestrales** (divisor \(n-1\)), como en EQS.

Generar ejemplos incluidos:

```bash
python scripts/build_examples.py
```

## Marco conceptual (cómo armar el estudio)

1. **Hipótesis** (ej. *la calidad impacta en la satisfacción*): debe fundamentarse con bibliografía que ya estudió la problemática. Regístrela en la hoja `Hipotesis`.
2. **Constructo / factor latente (F1, F2…)**: variable **no observable** (calidad, satisfacción). En el modelo aparece como factor; en los datos **no** tiene columna propia.
3. **Ítems / variables observadas**: respuestas de encuesta (clientes, usuarios). Cada constructo se **mide indirectamente** con **al menos 3 ítems** tomados de escalas ya validadas en literatura (hoja `Indicadores`).
4. **Escalas**: use ordinales (Likert 5 o 7 puntos). **No use ítems dicotómicos** (sí/no); el programa los rechaza.
5. **Datos**: hoja `Datos`, una columna por ítem (`CAL1`, `SAT1`, …).
6. **Descriptivos**: calcular media, varianza y **matriz de covarianzas** (`sem-tool descriptivos`).

### Tamaño de muestra (mínimo 100 respuestas)

Regla por defecto (habitual en investigación): **cada variable analizada debe tener al menos 100 observaciones** válidas en `Datos`. Configurable en **Config** → `observaciones_minimas`.

| Concepto | Significado |
|----------|-------------|
| **observaciones** (hoja Descriptivos) | n de respuestas no vacías por ítem |
| **observaciones_listwise** | n de filas completas usadas para la matriz de covarianzas |
| **cumple_muestra_minima** | Sí/No según el mínimo (100 por defecto) |

Si **n &lt; 100**, el análisis no se ejecuta. Si **100 ≤ n &lt; 200**, corre con advertencia (se recomienda ampliar para CB-SEM). PLS requiere **n ≥ 10** solo para bootstrap técnico; para inferencia fiable use **n ≥ 100**.

Ejemplo típico:

| Constructo latente | Factor | Ítems (≥3) | Hipótesis estructural |
|--------------------|--------|------------|------------------------|
| Calidad percibida | F1 / Calidad | CAL1–CAL4 | — |
| Satisfacción | F2 / Satisfaccion | SAT1–SAT4 | Calidad → Satisfacción |

## Hojas Excel

### `Datos`
Respuestas por encuesta: primera fila = nombres de ítems (variables observadas).

### `Hipotesis`
| origen | destino | hipotesis | referencia | argumento |
|--------|---------|-----------|------------|-----------|
| Calidad | Satisfaccion | H1: … | Autor (año) | Resumen teórico |

### `Indicadores`
Catálogo de ítems con escala y cita del instrumento.

| constructo | indicador | escala | puntos | referencia |
|------------|-----------|--------|--------|------------|
| Calidad | CAL1 | Likert | 5 | SERVQUAL (citar) |

### `Modelo_CB` (estilo EQS)

| tipo | lhs | op | rhs | label | fixed |
|------|-----|----|-----|-------|-------|
| medicion | Calidad | MEAS | CAL1 + CAL2 + CAL3 | | 1 |
| medicion | Satisfaccion | MEAS | SAT1 + SAT2 + SAT3 | | 1 |
| estructural | Satisfaccion | REG | Calidad | | |

- **MEAS** (o `=~` si exportás desde otro editor): carga factorial  
- **REG** (o `~`): regresión estructural  
- **COV** (o `~~`): covarianza residual  

> Excel convierte `=~` en fórmula; use **MEAS** / **REG** / **COV** en las celdas.
- `fixed=1` fija el primer indicador (identificación)

**Salidas:** `Fit_Indices`, `Criterios_Ajuste` (criterios de la lámina *The logic of the model fitness*), `Paths_Estandarizados`, `Paths_NoEstandarizados`, `Loadings`, `Warnings`

### Lógica del ajuste del modelo (fit)

| Tipo | Índices | Criterio habitual |
|------|---------|-------------------|
| **Absoluto** | χ² (p>0.05), χ² Satorra-Bentler, GFI, RMSR, RMSEA | RMSEA < 0.08; p no significativo |
| **Incremental** | NFI, TLI (NNFI), AGFI, CFI | > 0.90 (CFI ideal > 0.95) |
| **Parsimonioso** | χ² / gl | ≤ 5 |
| **Muestra** | N | N ≥ 5 × parámetros libres |

Hoja **`Criterios_Ajuste`**: criterios clásicos (lámina Frederic / Hu & Bentler 1999).

**Versión moderna (recomendada para informes actuales):**

| Hoja | Contenido |
|------|-----------|
| **`Criterios_Ajuste_Modernos`** | CFI/TLI ≥ 0.95, RMSEA ≤ 0.06, χ²/gl ≤ 3, χ² **Satorra-Bentler** |
| **`Informe_Ajuste_EQS`** | Salida tipo *GOODNESS OF FIT SUMMARY* (slides 37–38) |
| **`Criterios_Modernos_SEM`** | Tabla de referencia en plantilla |
| **`Enfoque_Moderno_CB_PLS`** | Cuándo usar CB robusto vs SmartPLS |

Plantilla clásica: **`Logica_Ajuste_Modelo`**.

## Sistema SmartPLS (PLS-SEM en sem-tool)

SmartPLS trabaja con **varianza explicada**, no con el ajuste global χ² de EQS. Flujo equivalente:

| Paso SmartPLS | Comando / hoja |
|---------------|----------------|
| Datos | `Datos` → `sem-tool descriptivos` |
| Especificar modelo | `Modelo_PLS` (ver plantilla **Sistema_SmartPLS**) |
| Calcular modelo | `sem-tool pls` |
| Bootstrap (5000) | `sem-tool pls -b 5000 -p 2` |
| Evaluar rutas | `Paths`, `Bootstraps`, **R2**, **Regresion_Structural** |
| Validez | `AVE_CR`, `Fornell_Larcker`, `HTMT`, `VIF` |

**CB vs PLS:** CB reproduce **S** (covarianzas) y usa **Fit_Indices**; PLS maximiza **R²** y usa **bootstrap + AVE/HTMT**. Puedes correr ambos en un mismo `.xlsx` (`sem-tool run-all`).

### `Modelo_PLS` (estilo SmartPLS)

| constructo | indicador | modo | ruta_origen | ruta_destino |
|------------|-----------|------|-------------|--------------|
| Calidad | CP1 | A | | |
| Calidad | | | Calidad | Lealtad |

- `modo`: **A** reflexivo, **B** formativo  
- Rutas: filas con `ruta_origen` y `ruta_destino` (indicador vacío)

**Salidas:** `Outer_Loadings`, `Paths`, `Bootstraps`, `R2`, `Efectos_f2`, `AVE_CR`, `Fornell_Larcker`, `HTMT`, `VIF`, `Warnings`

### `Config` (opcional)

| clave | valor |
|-------|-------|
| bootstraps | 5000 |
| procesos_bootstrap | 2 |

`bootstraps` debe ser múltiplo de `procesos_bootstrap` (requisito de `plspm`).

## Equivalencias EQS / SmartPLS

| EQS / SmartPLS | sem-tool |
|----------------|----------|
| Especificar cargas / paths en EQS | Filas en `Modelo_CB` |
| Diagrama de rutas SmartPLS | Filas `ruta_origen` → `ruta_destino` en `Modelo_PLS` |
| Reporte de fit (CFI, RMSEA…) | Hoja `Fit_Indices` |
| Outer loadings / bootstrapping | Hojas `Outer_Loadings`, `Bootstraps` |
| AVE, Fornell-Larcker, HTMT | Hojas homónimas |

## Validación automática

Antes de estimar, el programa comprueba:

- ≥ **3 ítems** por constructo / factor latente  
- **No dicotómicas** (máximo 2 valores distintos → error)  
- Ítems declarados en `Indicadores` y rutas documentadas en `Hipotesis` (advertencias si faltan)  

Los avisos aparecen en la hoja `Warnings`; los errores detienen el análisis.

## Ejemplos

- [`examples/ejemplo_cb_academico.xlsx`](examples/ejemplo_cb_academico.xlsx) — Calidad → Satisfacción (CB-SEM, Likert)  
- [`examples/ejemplo_pls_negocio.xlsx`](examples/ejemplo_pls_negocio.xlsx) — mismo modelo (PLS-SEM)  
- [`examples/estudio_calidad_satisfaccion.xlsx`](examples/estudio_calidad_satisfaccion.xlsx) — CB + PLS en un libro  

## GitHub y Streamlit (interfaz web)

### Subir a GitHub

```bash
cd /Users/claudiolarrea/Projects/sem-tool
git add .
git commit -m "sem-tool: CLI, Streamlit y CI"
git branch -M main
git remote add origin https://github.com/claudiomlarrea/sem-tool.git
git push -u origin main
```

Los archivos `taller_*.xlsx` y `mi_*.xlsx` locales están en `.gitignore` (no suben datos de encuesta). Sí se versionan `examples/` y `templates/`.

### App Streamlit en local

```bash
python3 -m pip install -e ".[web]"
streamlit run streamlit_app.py
```

Abre `http://localhost:8501`: descargar plantilla, subir Excel, ejecutar CB/PLS y descargar resultados.

### Publicar en Streamlit Cloud (gratis)

1. Repositorio en GitHub (público o privado con permisos).
2. [share.streamlit.io](https://share.streamlit.io) → **Create app**.
3. **Repository**: `claudiomlarrea/sem-tool`, **Branch**: `main`, **Main file**: `streamlit_app.py`.
4. **Requirements file**: `requirements.txt` (incluye `-e .` y `streamlit`).

Guía detallada: [`docs/DEPLOY.md`](docs/DEPLOY.md).

## Tests

```bash
pytest tests/ -m "not slow"
pytest tests/  # incluye ejemplos si existen
```

## Limitaciones (MVP)

- CB-SEM: microdatos; sin multi-grupo ni WLSMV robusto.  
- PLS: backend `plspm`; bootstrap pesado con 5000 iteraciones.  
- HTMT / Fornell-Larcker: implementación estándar simplificada para reporte en Excel.

## Licencia

Código del proyecto: uso académico/investigación. `plspm` es GPL-3.
