#!/usr/bin/env python3
# Mesma conta do servidor.py: entropia de Shannon do arquivo.
import collections
import math
import sys

data = open(sys.argv[1], "rb").read()
if not data:
    print("arquivo vazio.")
    sys.exit(0)
c = collections.Counter(data)
n = len(data)
e = -sum(v / n * math.log2(v / n) for v in c.values())
print("Entropia de Shannon: %.3f de 8.000  (%d bytes)\n"
      "Perto de 8 = bytes aleatorios (empacotado, comprimido ou cifrado)." % (e, n))
