#!/usr/bin/env bash
# Compila a amostra didatica do Caso 012 (ELF Linux, so indicadores, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o crypt_note fonte.c
echo "ok: $(pwd)/crypt_note"
file crypt_note
