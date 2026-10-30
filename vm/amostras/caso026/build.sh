#!/usr/bin/env bash
# Gera a amostra do Caso 026 (bytes de shellcode crus; nada a compilar).
set -e
cd "$(dirname "$0")"
python3 gerar.py
echo "ok: $(pwd)/shellcode.bin"
