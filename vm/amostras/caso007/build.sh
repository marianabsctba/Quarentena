#!/usr/bin/env bash
# Compila a amostra e anexa dados depois do fim do ELF (inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -o nota_fiscal fonte.c
cat overlay.bin >> nota_fiscal
rm -f overlay.bin
echo "ok: $(pwd)/nota_fiscal"
