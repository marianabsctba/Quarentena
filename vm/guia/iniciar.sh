#!/usr/bin/env bash
# Inicia o Quarentena dentro da VM: compila a amostra, sobe o servidor local
# e abre o navegador no ambiente 3D. (O servidor so escuta em 127.0.0.1.)
set -e
cd "$(dirname "$0")"
# compila/gera todas as amostras (cada uma e inofensiva); ignora falha isolada
for b in ../amostras/caso*/build.sh; do bash "$b" >/dev/null 2>&1 || true; done
python3 servidor.py &
SRV=$!
sleep 1
URL="http://127.0.0.1:8777"
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v sensible-browser >/dev/null 2>&1; then sensible-browser "$URL" >/dev/null 2>&1 || true
else echo "Abra no navegador: $URL"; fi
echo "Quarentena rodando. Ctrl+C para encerrar."
wait $SRV
