#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 006: payload comprimido. O "modulo" anexo e, na verdade, dados gzip.
# Compactar nao e criptografia: basta descomprimir pra ler a config e o C2.
# INOFENSIVO: so texto de config dentro do gzip.
import gzip
conf = (b"# modulo de atualizacao (amostra DIDATICA, inofensiva)\n"
        b"C2=http://gz-c2.example.org/beacon\n"
        b"intervalo=60\n")
open("modulo_extra.bin", "wb").write(gzip.compress(conf))
print("modulo_extra.bin (gzip) gerado")
