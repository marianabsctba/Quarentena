#!/usr/bin/env bash
# Gera a amostra do Caso 006 (um arquivo gzip; nao ha binario a compilar).
set -e
cd "$(dirname "$0")"
python3 gerar.py
echo "ok: $(pwd)/modulo_extra.bin"
file modulo_extra.bin
