#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 002: HEXADECIMAL embutido no binario. A config fica codificada em hex
# (aparece no strings como digitos 0-9 e a-f), e o aluno decodifica. INOFENSIVO.
# Diferente do base64: aqui cada par de digitos e um byte.
C2 = "http://config.bad-update.xyz/c"
h = C2.encode().hex()
fonte = '''// Amostra 002 (hexadecimal embutido) da Panthera Quarentena - INOFENSIVA.
#include <stdio.h>
static char cfg[] = "%s";  /* endpoint de config, em hexadecimal */
int main(void) { (void)cfg; puts("Amostra 002 (hex embutido). Inofensiva."); return 0; }
''' % h
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada (hex de %r)" % C2)
