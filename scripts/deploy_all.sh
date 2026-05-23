#!/usr/bin/env bash
# Despliegue completo: GitHub + instrucciones Streamlit Cloud
# Uso: ./scripts/deploy_all.sh
set -euo pipefail

REPO_NAME="${REPO_NAME:-sem-tool}"
GITHUB_USER="${GITHUB_USER:-claudiomlarrea}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> sem-tool deploy (usuario GitHub: $GITHUB_USER)"

if ! command -v gh >/dev/null 2>&1; then
  echo "Instale GitHub CLI: brew install gh"
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  if [[ -n "${GH_TOKEN:-}" || -n "${GITHUB_TOKEN:-}" ]]; then
    printf '%s' "${GH_TOKEN:-$GITHUB_TOKEN}" | gh auth login -h github.com --with-token
  else
    echo "No hay sesión de GitHub. Ejecute en su terminal:"
    echo "  gh auth login -h github.com -p https -w"
    echo "Luego vuelva a correr: ./scripts/deploy_all.sh"
    exit 1
  fi
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  git init
  git branch -M main
fi

if ! git rev-parse HEAD >/dev/null 2>&1; then
  git add .
  git commit -m "sem-tool: CLI, Streamlit, CI y documentación"
fi

REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

if gh repo view "${GITHUB_USER}/${REPO_NAME}" >/dev/null 2>&1; then
  echo "==> Repositorio ya existe; push..."
  git push -u origin main
else
  echo "==> Creando repositorio público y subiendo..."
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
fi

echo ""
echo "✓ GitHub: https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "==> Streamlit Cloud (manual, 2 minutos):"
echo "  1. https://share.streamlit.io"
echo "  2. New app → ${GITHUB_USER}/${REPO_NAME} → main → streamlit_app.py"
echo "  3. Requirements: requirements.txt → Deploy"
echo ""
