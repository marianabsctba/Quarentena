#!/usr/bin/env python3
# Amostra didatica (overlay) - INOFENSIVA. O programa nao le o proprio overlay:
# os dados so ficam la, depois do fim do ELF, para o aluno encontrar.
import base64

CONFIG = "c2=http://overlay-c2.example.net/x;campanha=NF2026"

fonte = '''// Amostra didatica (overlay) - INOFENSIVA. Gerada por gerar.py.
#include <stdio.h>
int main(void) {
    puts("Nota fiscal 2026-0042 emitida. (Amostra didatica, inofensiva.)");
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
with open("overlay.bin", "w", encoding="ascii") as f:
    f.write("\nPQ_OVERLAY_v1\n" + base64.b64encode(CONFIG.encode()).decode() + "\n")
print("fonte.c e overlay.bin gerados")
