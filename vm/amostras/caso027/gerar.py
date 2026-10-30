#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 027 (mestre): API HASHING. INOFENSIVO.
# Em vez de importar a funcao pelo nome (o que apareceria no readelf e entregaria
# a capacidade), o binario guarda so um HASH do nome e resolve em runtime. Isso
# esconde do analista o que ele usa. A amostra NAO chama nada perigoso: so
# demonstra a tecnica com uma funcao benigna (getenv). O aluno le o algoritmo de
# hash no Ghidra, pega o hash guardado e descobre QUAL nome bate.
def djb2(s):
    h = 5381
    for c in s.encode():
        h = ((h * 33) + c) & 0xffffffff
    return h

ALVO = "getenv"            # funcao benigna resolvida por hash
H = djb2(ALVO)
fonte = '''// Amostra 027 (API hashing) da Panthera Quarentena - INOFENSIVA.
// Resolve uma funcao pelo HASH do nome (djb2), nao pelo nome. Aqui o alvo e
// 'getenv' (benigno) e nada e chamado: so demonstra a tecnica de ofuscacao.
#include <stdio.h>
#include <string.h>

static unsigned int djb2(const char *s){
    unsigned int h = 5381; int i;
    for (i = 0; s[i]; i++) h = (h * 33) + (unsigned char)s[i];
    return h;
}

int main(void){
    /* O hash do nome fica como imediato no codigo (visivel no objdump/Ghidra).
       Num malware real, um loop compararia djb2(nome) da libc com este valor e
       chamaria o que casasse. Aqui nada e chamado: so demonstra a tecnica. */
    volatile unsigned int alvo_hash = 0x%08xu;   /* hash do nome da API escondida */
    (void)djb2;
    printf("Amostra 027 (API hashing). Inofensiva.\\n");
    return (int)(alvo_hash & 0u);
}
''' % H
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c 027 gerada. ALVO=%r djb2=0x%08x" % (ALVO, H))
