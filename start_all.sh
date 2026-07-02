#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT="8000"
FRONTEND_PORT="4200"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "==> Preparando entorno Python"
if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements.txt"

echo "==> Preparando frontend Angular"
cd "$FRONTEND_DIR"
if [[ ! -d node_modules ]]; then
  npm install
fi
cd "$ROOT_DIR"

echo "==> Aplicando migraciones"
python manage.py migrate --noinput

echo "==> Iniciando backend Django en http://127.0.0.1:${BACKEND_PORT}"
python manage.py runserver 0.0.0.0:${BACKEND_PORT} &
BACKEND_PID=$!

echo "==> Iniciando frontend Angular en http://localhost:${FRONTEND_PORT}"
( cd "$FRONTEND_DIR" && npm run start -- --host 0.0.0.0 --port ${FRONTEND_PORT} ) &
FRONTEND_PID=$!

echo ""
echo "Backend PID: ${BACKEND_PID}"
echo "Frontend PID: ${FRONTEND_PID}"
echo ""
echo "Abre http://localhost:${FRONTEND_PORT}/"
echo "Presiona Ctrl+C para detener ambos servicios."

wait "$BACKEND_PID" "$FRONTEND_PID"
