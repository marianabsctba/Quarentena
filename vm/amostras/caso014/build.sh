#!/usr/bin/env bash
# Compila a amostra do Caso 014 (ELF Linux, anti-sandbox, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o env_check fonte.c
echo "ok: $(pwd)/env_check"
file env_check
