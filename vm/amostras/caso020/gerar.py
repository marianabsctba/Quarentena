#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera a fonte C da amostra didatica do Caso 020 (avancada) - INOFENSIVA.
#
# Sobe a dificuldade em relacao aos casos anteriores:
#   - XOR de CHAVE MULTI-BYTE (4 bytes "BSC!"), nao mais 1 byte;
#   - checagem de ANTI-VM (le o nome do produto em /sys .../dmi), alem do
#     anti-debug com ptrace;
#   - o binario e STRIPPED no build (sem nomes de funcao), entao o aluno tem
#     que ler o codigo cru, sem simbolos ajudando.
# Continua inofensiva: nao conecta, nao persiste de verdade, nao ataca.

C2 = "http://patch-update.ddns.net/beacon"
KEY = b"BSC!"

enc = bytes(c ^ KEY[i % len(KEY)] for i, c in enumerate(C2.encode()))
enc_arr = ", ".join("0x%02x" % b for b in enc)
key_arr = ", ".join("0x%02x" % b for b in KEY)

fonte = '''// Amostra didatica da Panthera Quarentena - Caso 020 (avancada) - INOFENSIVA.
// Gerada por gerar.py. XOR multi-byte + anti-debug + anti-VM. Compilada
// STRIPPED para treino de leitura sem simbolos. Nao faz nada malicioso.
#include <stdio.h>
#include <string.h>
#include <sys/ptrace.h>

static unsigned char enc[] = { %s };
static unsigned char key[] = { %s };

static void decode(char *out, const unsigned char *in, int n) {
    int i;
    for (i = 0; i < n; i++) out[i] = in[i] ^ key[i %% 4];
    out[n] = 0;
}

static int anti_debug(void) {
    return ptrace(PTRACE_TRACEME, 0, 0, 0) == -1;
}

static int anti_vm(void) {
    FILE *f = fopen("/sys/devices/virtual/dmi/id/product_name", "r");
    if (!f) return 0;
    char b[64] = {0};
    if (!fgets(b, 63, f)) { fclose(f); return 0; }
    fclose(f);
    return (strstr(b, "VirtualBox") || strstr(b, "VMware")) ? 1 : 0;
}

static void beacon(const char *url) {
    fprintf(stderr, "[amostra] beacon -> %%s\\n", url);
}

int main(int argc, char **argv) {
    char url[128];
    decode(url, enc, sizeof(enc));
    if (argc > 1 && strcmp(argv[1], "--arm") == 0) {
        if (anti_debug()) return 0;
        if (anti_vm()) { puts("ambiente virtual detectado, dormindo."); return 0; }
        FILE *f = fopen("/tmp/panthera_stage.txt", "w");
        if (f) { fputs("marcador didatico (inofensivo)\\n", f); fclose(f); }
        beacon(url);
    } else {
        puts("Amostra 020 da Panthera Quarentena (avancada). Inofensiva e sem simbolos.");
    }
    return 0;
}
''' % (enc_arr, key_arr)

with open("fonte.c", "w", encoding="utf-8") as f:
    f.write(fonte)

print("fonte.c gerada. C2 com XOR de chave %r, %d bytes." % (KEY.decode(), len(enc)))
