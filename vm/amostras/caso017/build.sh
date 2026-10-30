#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 gerar.py
echo "ok: $(pwd)/dga.py"
