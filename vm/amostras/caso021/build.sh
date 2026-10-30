#!/usr/bin/env bash
# Compila a amostra do Caso 021 (ELF Linux, RC4, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o rc4_loader fonte.c
echo "ok: $(pwd)/rc4_loader"
file rc4_loader
