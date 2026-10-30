#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -o updater fonte.c
echo "ok: $(pwd)/updater"
