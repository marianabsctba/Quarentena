#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 019: ANTI-DEBUG via /proc/self/status (campo TracerPid). Variante do
# anti-debug sem ptrace: o programa le /proc/self/status e, se TracerPid for
# diferente de zero, sabe que tem um debugger anexado. INOFENSIVO.
fonte = '''// Amostra 019 (anti-debug via TracerPid) da Panthera Quarentena - INOFENSIVA.
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static int debugged(void) {
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;
    char l[256];
    while (fgets(l, sizeof l, f)) {
        if (strncmp(l, "TracerPid:", 10) == 0) {
            int p = atoi(l + 10);
            fclose(f);
            return p != 0;
        }
    }
    fclose(f);
    return 0;
}

int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "--arm") == 0) {
        if (debugged()) { puts("debugger detectado, abortando."); return 0; }
        fprintf(stderr, "[amostra] sem debugger; seguiria o fluxo\\n");
    } else {
        puts("Amostra 019 (anti-debug via TracerPid). Inofensiva.");
    }
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada (anti-debug TracerPid)")
