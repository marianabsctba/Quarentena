#!/usr/bin/env bash
# Compila a amostra de disfarce de processo (inofensiva).
set -e
cd "$(dirname "$0")"
python3 gerar.py
gcc -O0 -no-pie -fno-stack-protector -o svc_helper fonte.c
echo "ok: $(pwd)/svc_helper"
