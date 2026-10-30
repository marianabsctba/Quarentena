#!/usr/bin/env bash
# Compila e EMPACOTA a amostra do Caso UPX (ELF Linux, inofensiva).
# Precisa do 'upx' (upx-ucl). Sem ele, deixa o binario SEM empacotar e avisa.
set -e
cd "$(dirname "$0")"
python3 gerar.py
# -fcf-protection=none e -Wl,-z,noseparate-code removem secoes (CET / .note.gnu
# .property / segmento separate-code) que o upx 3.96 do Ubuntu 22.04 nao engole.
gcc -O0 -no-pie -fno-stack-protector -fcf-protection=none -Wl,-z,noseparate-code \
    -o .tmp_unpacked fonte.c
if command -v upx >/dev/null 2>&1; then
    rm -f packed_update
    upx -9 -q -o packed_update .tmp_unpacked >/dev/null
    rm -f .tmp_unpacked
    echo "ok (empacotado com UPX): $(pwd)/packed_update"
else
    mv -f .tmp_unpacked packed_update
    echo "AVISO: 'upx' nao instalado; 'packed_update' ficou SEM empacotar."
    echo "       Instale upx-ucl (provision.sh faz isso na VM) e rode de novo."
fi
file packed_update
