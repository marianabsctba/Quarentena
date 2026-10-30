#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 014 (intermediario): ANTI-SANDBOX por recursos e tempo. INOFENSIVO.
# Diferente do anti-debug (001/015) e do anti-VM por DMI (003): aqui o truque e
# contar CPUs (sandbox costuma ter poucas) e dormir pra "furar" analises
# automaticas curtas. O binario le /sys/devices/system/cpu/online, compara com
# um minimo (2) e so segue se tiver CPUs suficientes. Nao faz nada malicioso.
MIN_CPUS = 2
fonte = '''// Amostra 014 (anti-sandbox) da Panthera Quarentena - INOFENSIVA. Gerada por gerar.py.
// Conta CPUs lendo /sys e dorme um pouco: evasao de sandbox. So imprime texto.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int contar_cpus(void) {
    FILE *f = fopen("/sys/devices/system/cpu/online", "r");  /* conta nucleos */
    char buf[64] = {0};
    int lo = 0, hi = 0;
    if (!f) return 1;
    if (fgets(buf, sizeof(buf), f)) {
        if (sscanf(buf, "%%d-%%d", &lo, &hi) == 2) { fclose(f); return hi - lo + 1; }
        fclose(f); return 1;
    }
    fclose(f);
    return 1;
}

int main(void) {
    int cpus = contar_cpus();
    sleep(1);                         /* atraso: cansa sandbox de analise curta */
    if (cpus < %d) {                  /* poucas CPUs = provavel sandbox */
        puts("ambiente de analise detectado; encerrando.");
        return 0;
    }
    puts("ambiente real; prosseguindo.");
    return 0;
}
''' % MIN_CPUS
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada (le /sys/devices/system/cpu/online, minimo=%d CPUs, sleep)." % MIN_CPUS)
