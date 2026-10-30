#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 023 (avancado): ELF AUTO-DECODIFICANTE. INOFENSIVO.
# A string nao esta em XOR de chave fixa (como 001/003): esta "empacotada" com
# uma cifra de feedback (a chave MUDA a cada byte). Em estatica aparece lixo;
# pra desempacotar, o aluno tem que REPLICAR o algoritmo do stub de decode,
# nao basta um XOR simples. Nada e executado de malicioso.
PLAIN = "STAGE2::http://selfdec-c2.example.org/s"

# Cifra de feedback: k comeca em 0x7F; cada saida = c ^ k; depois k = (k+7)&0xff
def encode(s):
    k = 0x7F; out = bytearray()
    for ch in s.encode():
        out.append(ch ^ k)
        k = (k + 7) & 0xff
    return bytes(out)


def decode(b):
    k = 0x7F; out = bytearray()
    for c in b:
        out.append(c ^ k)
        k = (k + 7) & 0xff
    return bytes(out)


enc = encode(PLAIN)
assert decode(enc) == PLAIN.encode(), "feedback nao reversivel?!"
enc_arr = ", ".join("0x%02x" % b for b in enc)

fonte = '''// Amostra 023 (auto-decodificante) da Panthera Quarentena - INOFENSIVA.
// Gerada por gerar.py. O stub decodifica o blob em memoria com uma cifra de
// FEEDBACK (a chave evolui a cada byte). Estatica ve lixo; so replicando o
// algoritmo se desempacota. Nao conecta, nao persiste.
#include <stdio.h>

static unsigned char blob[] = { %s };
static char out[128];

int main(void) {
    int i, n = (int)sizeof(blob);
    unsigned char k = 0x7F;      /* chave inicial */
    for (i = 0; i < n; i++) {
        out[i] = (char)(blob[i] ^ k);
        k = (unsigned char)((k + 7) & 0xff);   /* feedback: a chave anda */
    }
    out[n] = 0;
    puts("stage2 desempacotado em memoria.");  /* nao revela o conteudo */
    return 0;
}
''' % enc_arr

open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada. plano=%r" % PLAIN)
print("blob (hex):", enc.hex())
