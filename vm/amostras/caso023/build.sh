#!/usr/bin/env bash
# Compila a amostra do Caso 023 (ELF Linux, auto-decodificante, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o selfdec fonte.c
echo "ok: $(pwd)/selfdec"
file selfdec
