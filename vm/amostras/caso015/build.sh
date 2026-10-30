#!/usr/bin/env bash
# Gera a amostra do Caso 015 (uma captura de rede .pcap; nao ha binario).
set -e
cd "$(dirname "$0")"
python3 gerar.py
echo "ok: $(pwd)/captura.pcap"
