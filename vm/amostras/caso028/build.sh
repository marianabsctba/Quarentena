#!/usr/bin/env bash
# Gera a amostra do Caso 028 (captura .pcap com C2 cifrado; nada a compilar).
set -e
cd "$(dirname "$0")"
python3 gerar.py
echo "ok: $(pwd)/c2.pcap"
