#!/usr/bin/env bash
# Compila o fonte Python em bytecode e entrega so o .pyc (inofensivo).
set -e
cd "$(dirname "$0")"
python3 gerar.py
python3 -c "import py_compile; py_compile.compile('agente_fonte.py', cfile='agente.pyc')"
rm -f agente_fonte.py
echo "ok: $(pwd)/agente.pyc"
