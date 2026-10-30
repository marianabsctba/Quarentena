#!/usr/bin/env bash
# Compila a amostra didatica do Caso 030 (ELF Linux, capstone, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o sample_x fonte.c
echo "ok: $(pwd)/sample_x"
file sample_x
