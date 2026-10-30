#!/usr/bin/env bash
# Compila a amostra didatica do Caso 025 (ELF Linux, indicadores de injecao).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o mem_tool fonte.c
echo "ok: $(pwd)/mem_tool"
file mem_tool
