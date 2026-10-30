#!/usr/bin/env bash
# Compila a amostra didatica do Caso 027 (ELF Linux, API hashing, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o resolver fonte.c
echo "ok: $(pwd)/resolver"
file resolver
