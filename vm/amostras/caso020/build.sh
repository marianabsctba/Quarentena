#!/usr/bin/env bash
# Compila a amostra do Caso 020 (ELF Linux, STRIPPED, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o patch_update fonte.c
strip patch_update           # remove os simbolos (sobe a dificuldade)
echo "ok: $(pwd)/patch_update"
file patch_update
