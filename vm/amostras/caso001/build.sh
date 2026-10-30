#!/usr/bin/env bash
# Compila a amostra didatica do Caso 001 (ELF Linux, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
# -O0 e sem PIE/stack-protector para o codigo ficar mais legivel no Ghidra/radare2.
gcc -O0 -no-pie -fno-stack-protector -o fatura_outubro fonte.c
echo "ok: $(pwd)/fatura_outubro"
file fatura_outubro
