#!/usr/bin/env bash
# Compila a amostra de trava de execucao (inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o licenca_check fonte.c
echo "ok: $(pwd)/licenca_check"
