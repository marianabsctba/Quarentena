#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 gerar.py
chmod +x conexao_suporte.sh 2>/dev/null || true
echo "ok: $(pwd)/conexao_suporte.sh"
