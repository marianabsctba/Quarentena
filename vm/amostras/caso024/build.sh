#!/usr/bin/env bash
# Compila a amostra com construtor antes da main (inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o boot_tool fonte.c
echo "ok: $(pwd)/boot_tool"
