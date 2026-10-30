#!/usr/bin/env python3
# Amostra didatica (disfarce de processo) - INOFENSIVA. So troca o proprio nome
# e mostra o resultado; nao persiste, nao fala com a rede.
fonte = '''// Amostra didatica (disfarce de processo) - INOFENSIVA. Gerada por gerar.py.
#include <stdio.h>
#include <string.h>
#include <sys/prctl.h>

int main(int argc, char **argv) {
    char nome[32] = {0};
    FILE *f;
    if (argc < 2 || strcmp(argv[1], "--arm") != 0) {
        puts("Amostra didatica (disfarce de processo). Inofensiva.");
        return 0;
    }
    prctl(PR_SET_NAME, "[kworker/0:1]", 0, 0, 0);
    f = fopen("/proc/self/comm", "r");
    if (f) { fgets(nome, sizeof(nome), f); fclose(f); }
    printf("agora o sistema me chama de: %s", nome);
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada")
