#!/usr/bin/env python3
# Amostra didatica (construtor antes da main) - INOFENSIVA. O construtor so checa
# depurador e grava um marcador em /tmp; a main parece um programa comum.
fonte = '''// Amostra didatica (construtor) - INOFENSIVA. Gerada por gerar.py.
#include <stdio.h>
#include <unistd.h>
#include <sys/ptrace.h>

static int armada = 0;

__attribute__((constructor)) void pre_main(void) {
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) _exit(0);
    FILE *f = fopen("/tmp/panthera_ctor.txt", "w");
    if (f) { fputs("marcador didatico (inofensivo)\\n", f); fclose(f); }
    armada = 1;
}

int main(void) {
    puts(armada ? "Ferramenta de boot: tudo certo." : "Ferramenta de boot.");
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada")
