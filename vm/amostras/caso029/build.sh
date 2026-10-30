#!/usr/bin/env bash
# Gera a amostra do Caso 029 (captura .pcap de protocolo proprio; nada a compilar).
set -e
cd "$(dirname "$0")"
python3 gerar.py
echo "ok: $(pwd)/proto.pcap"
