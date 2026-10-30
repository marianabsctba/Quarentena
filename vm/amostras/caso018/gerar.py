#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera a fonte C da amostra didatica do Caso 018 - INOFENSIVA.
#
# Tecnica nova: STACK STRINGS. O endereco de C2 nao existe como texto no
# binario; ele e montado caractere por caractere na pilha em tempo de execucao
# (cada letra vira um 'mov byte' no codigo). Por isso o 'strings' NAO acha nada,
# e o analista precisa LER o codigo (ver os bytes imediatos) ou RODAR a amostra.
# E uma evasao real de deteccao baseada em strings. Continua inofensiva.

C2 = "http://cdn.sync-updates.workers.dev/g"

asg = "".join("    u[i++] = %d; /* %s */\n" % (ord(c), c if c.isprintable() and c != '*' else '.') for c in C2)

fonte = '''// Amostra didatica da Panthera Quarentena - Caso 018 (stack strings) - INOFENSIVA.
// Gerada por gerar.py. O C2 e montado byte a byte na pilha, entao nao aparece
// no 'strings'. Para revelar: leia o codigo (bytes imediatos) ou rode a amostra.
#include <stdio.h>

int main(void) {
    char u[64];
    int i = 0;
%s    u[i] = 0;
    fprintf(stderr, "config endpoint: %%s\\n", u);
    puts("Amostra 018 (stack strings) da Panthera Quarentena. Inofensiva.");
    return 0;
}
''' % asg

with open("fonte.c", "w", encoding="utf-8") as f:
    f.write(fonte)

print("fonte.c gerada. C2 montado como stack string (%d bytes)." % len(C2))
