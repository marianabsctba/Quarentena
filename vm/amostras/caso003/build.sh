#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -o net_check fonte.c
echo "ok: $(pwd)/net_check"
