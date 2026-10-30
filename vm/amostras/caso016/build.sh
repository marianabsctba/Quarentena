#!/usr/bin/env bash
# Gera a amostra do Caso 016 (captura .pcap de DNS tunneling, inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
echo "ok: $(pwd)/tunnel.pcap"
