#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 004: ENTROPIA e deteccao de empacotamento. ELF com um grande bloco de
# bytes aleatorios (como um payload cifrado/comprimido), elevando a entropia do
# arquivo. INOFENSIVO. Ensina: entropia perto de 8 = dados aleatorios = sinal de
# empacotamento ou cifra.
import os
rnd = os.urandom(49152)
arr = ",".join(str(b) for b in rnd)
fonte = '''// Amostra 004 (entropia alta) da Panthera Quarentena - INOFENSIVA.
#include <stdio.h>
static const unsigned char blob[] = { %s };
int main(void) { (void)blob; puts("Amostra 004 (entropia alta). Inofensiva."); return 0; }
''' % arr
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada (%d bytes aleatorios embutidos)" % len(rnd))
