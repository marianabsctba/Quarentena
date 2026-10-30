#!/usr/bin/env python3
# Amostra didatica (trava de execucao) - INOFENSIVA. Mesmo no host "certo", ela
# so imprime uma mensagem: a trava existe para o aluno aprender a reconhecer.
fonte = '''// Amostra didatica (trava de execucao) - INOFENSIVA. Gerada por gerar.py.
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv) {
    char host[64] = {0};
    if (argc < 2 || strcmp(argv[1], "--arm") != 0) return 0;
    gethostname(host, sizeof(host) - 1);
    if (strcmp(host, "FIN-SRV-01") != 0) return 0;
    puts("[amostra] alvo confirmado (didatico, nada aconteceu).");
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada")
