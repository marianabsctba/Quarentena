#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 021 (avancado): RC4 de verdade embutido no ELF. INOFENSIVO.
# Diferente do Caso 021 (hex) e do 001/003 (XOR): aqui e CRIPTOGRAFIA de
# fluxo (RC4). O binario carrega a chave (string visivel) e o texto cifrado
# (em hex), e um RC4 classico que decifra em memoria. O aluno le o RC4 no
# Ghidra/objdump, pega a chave e o blob, e decifra offline pra achar o C2.
C2 = "http://rc4-c2.example.net/k"
KEY = b"panthera_rc4"


def rc4(key, data):
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xff
        S[i], S[j] = S[j], S[i]
    out = bytearray(); i = j = 0
    for c in data:
        i = (i + 1) & 0xff
        j = (j + S[i]) & 0xff
        S[i], S[j] = S[j], S[i]
        out.append(c ^ S[(S[i] + S[j]) & 0xff])
    return bytes(out)


ct = rc4(KEY, C2.encode())
ct_hex = ct.hex()
assert rc4(KEY, ct) == C2.encode(), "RC4 nao e reversivel?!"

fonte = '''// Amostra 021 (RC4) da Panthera Quarentena - INOFENSIVA. Gerada por gerar.py.
// RC4 classico decifra o endpoint em memoria. Nao conecta em lugar nenhum.
#include <stdio.h>
#include <string.h>

static unsigned char key[] = "%s";          /* chave RC4 (visivel no strings) */
static char ct_hex[] = "%s";                /* texto cifrado, em hexadecimal */
static unsigned char out[64];

static int unhex(const char *h, unsigned char *b) {
    int i, n = (int)strlen(h) / 2;
    for (i = 0; i < n; i++) sscanf(h + 2 * i, "%%2hhx", &b[i]);
    return n;
}

static void rc4(unsigned char *S, const unsigned char *k, int klen) {
    int i, j = 0; unsigned char t;
    for (i = 0; i < 256; i++) S[i] = (unsigned char)i;
    for (i = 0; i < 256; i++) {
        j = (j + S[i] + k[i %% klen]) & 0xff;
        t = S[i]; S[i] = S[j]; S[j] = t;
    }
}

int main(void) {
    unsigned char ct[64], S[256];
    int n = unhex(ct_hex, ct), i = 0, j = 0, x;
    unsigned char t;
    rc4(S, key, (int)strlen((char *)key));
    for (x = 0; x < n; x++) {
        i = (i + 1) & 0xff;
        j = (j + S[i]) & 0xff;
        t = S[i]; S[i] = S[j]; S[j] = t;
        out[x] = ct[x] ^ S[(S[i] + S[j]) & 0xff];
    }
    out[n] = 0;
    puts("config carregada.");   /* nao imprime o endpoint: inofensiva */
    return 0;
}
''' % (KEY.decode(), ct_hex)

open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada. chave=%r, C2=%r, ct_hex=%s" % (KEY.decode(), C2, ct_hex))
