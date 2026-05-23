# Despliegue: GitHub + Streamlit Cloud

## 1. Repositorio GitHub

```bash
git init   # solo si aún no hay repo
git add .
git commit -m "sem-tool: CB-SEM, PLS-SEM, Streamlit"
git branch -M main
git remote add origin https://github.com/claudiomlarrea/sem-tool.git
git push -u origin main
```

### Qué no subir

- Libros con datos reales de encuesta (`taller_*.xlsx`, `mi_*.xlsx`) — ya en `.gitignore`.
- `.venv/`, `__pycache__/`, `.pytest_cache/`.

### CI

Cada push a `main` ejecuta `.github/workflows/ci.yml` (pytest en Python 3.9 y 3.11).

## 2. Streamlit local

```bash
python3 -m pip install -e ".[web]"
streamlit run streamlit_app.py
```

## 3. Streamlit Cloud

| Campo | Valor |
|-------|--------|
| Main file | **`streamlit_app.py`** (no `scripts/build_examples.py`) |
| Requirements | `requirements.txt` |
| Python | **3.11** (archivo `.python-version`; evitar 3.14 con `plspm`) |

**Notas**

- PLS con bootstrap alto (5000+) puede superar el límite de tiempo de la app gratuita; use 500–1000 en la web.
- La app escribe en directorio temporal; el usuario descarga el Excel final (no persiste en servidor).

## 4. Alternativas

- **Solo CLI**: `python3 -m sem_tool run-all estudio.xlsx`
- **Docker** (futuro): imagen con `streamlit run` + volumen para Excel.
