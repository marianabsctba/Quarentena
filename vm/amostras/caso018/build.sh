#!/usr/bin/env bash
# Compila a amostra do Caso 018 (ELF Linux, stack strings, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
# -O0 para preservar as atribuicoes byte a byte (a stack string) no codigo.
gcc -O0 -no-pie -fno-stack-protector -o config_loader fonte.c
echo "ok: $(pwd)/config_loader"
