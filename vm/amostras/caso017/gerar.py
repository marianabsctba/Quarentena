#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 017: DGA (Domain Generation Algorithm). Um script que gera dominios
# pseudo-aleatorios a partir de uma seed. O analista reverte o algoritmo e
# consegue PREVER os dominios futuros (pra bloquear antes). INOFENSIVO.
sample = '''#!/usr/bin/env python3
# dga.py - amostra didatica da Panthera Quarentena (Caso 017) - INOFENSIVA.
# Gera dominios pseudo-aleatorios (como um DGA de verdade). Nada e contatado.
import sys

def gen(seed, n=5):
    x = seed & 0x7fffffff
    out = []
    for _ in range(n):
        x = (x * 1103515245 + 12345) & 0x7fffffff
        name = "".join("abcdefghijklmnopqrstuvwxyz"[(x >> (j * 5)) % 26] for j in range(8))
        out.append(name + ".xyz")
    return out

if __name__ == "__main__":
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 1337
    for d in gen(s):
        print(d)
'''
open("dga.py", "w", encoding="utf-8").write(sample)
print("gerado dga.py (DGA)")
