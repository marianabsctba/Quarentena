#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 010: CREDENTIAL STEALER. ELF que, em modo --arm, apenas ABRE arquivos de
# credenciais (/etc/passwd e ~/.ssh/id_rsa). INOFENSIVO: nao le conteudo nem
# exfiltra nada; so toca nos caminhos para o aluno ver no strace o que ele mira.
fonte = '''// Amostra 010 (credential stealer) da Panthera Quarentena - INOFENSIVA.
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "--arm") == 0) {
        FILE *f = fopen("/etc/passwd", "r"); if (f) fclose(f);
        const char *h = getenv("HOME");
        char p[256]; snprintf(p, sizeof p, "%s/.ssh/id_rsa", h ? h : "/root");
        FILE *k = fopen(p, "r"); if (k) fclose(k);
        fprintf(stderr, "[amostra] tocou em /etc/passwd e ~/.ssh/id_rsa (didatico, nada exfiltrado)\\n");
    } else {
        puts("Amostra 010 (credential stealer). Inofensiva.");
    }
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada (credential stealer)")
