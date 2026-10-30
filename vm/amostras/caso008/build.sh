#!/usr/bin/env bash
# "Compila" a amostra do Caso 008 (so gera o script; nao ha binario).
set -e
cd "$(dirname "$0")"
python3 gerar.py
chmod +x atualizacao_sistema.sh 2>/dev/null || true
echo "ok: $(pwd)/atualizacao_sistema.sh"
