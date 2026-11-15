#!/usr/bin/env bash
# LaCakes – sobe o sistema com um comando (Linux/macOS): ./iniciar.sh
# Opcional: ./iniciar.sh --recriar  (apaga os pedidos e volta o banco ao estado inicial)
set -e
cd "$(dirname "$0")"

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

if [ ! -x .venv/bin/python ]; then
  echo "[1/3] Criando ambiente virtual..."
  $PY -m venv .venv
fi
echo "[2/3] Instalando dependências..."
.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements.txt
echo "[3/3] Preparando o banco de dados..."
.venv/bin/python -m app.seed "$@"
.venv/bin/python run.py
