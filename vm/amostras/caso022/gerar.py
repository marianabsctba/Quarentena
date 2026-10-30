#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso UPX (avancado): PACKING com UPX. INOFENSIVO.
# gerar.py so escreve a fonte C (com um C2 escondido) + um bloco grande e
# repetitivo pra o binario ter tamanho/redundancia suficiente pro UPX empacotar
# (binario minusculo da 'NotCompressibleException'). O build.sh compila e
# empacota com upx: strings some (menos a marca "UPX!") e a entropia sobe. O
# aluno reconhece o packer e roda 'upx -d' pra desempacotar e ler o C2.
C2 = "http://upx-c2.example.com/u"
# ~180 KB repetitivos: enche o binario e e muito compressivel (UPX adora).
PAD = "amostra-didatica-panthera-quarentena-" * 6000
fonte = '''// Amostra UPX (packing) da Panthera Quarentena - INOFENSIVA.
// Guarda um C2 numa string; depois de empacotado com UPX ele some das strings
// e so reaparece apos 'upx -d'. O 'pad' enche o binario pro UPX ter o que
// comprimir. Nao conecta em lugar nenhum.
#include <stdio.h>
static const char cfg[] = "%s";   /* C2, vai sumir apos o packing */
static const char pad[] = "%s";   /* enchimento compressivel */
int main(void){ (void)cfg; (void)pad; puts("Amostra UPX (packing). Inofensiva."); return 0; }
''' % (C2, PAD)
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada. C2 escondido=%s (pad=%d bytes)" % (C2, len(PAD)))
