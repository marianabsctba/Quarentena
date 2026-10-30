#!/usr/bin/env python3
# Amostra didatica (bytecode Python) - INOFENSIVA. Nada de rede: destino() so
# monta um texto e nunca e chamada. O aluno recebe apenas o .pyc, sem o fonte.
fonte = '''# Amostra didatica (bytecode) - INOFENSIVA. Gerada por gerar.py.
def destino():
    partes = ["http://", "pyc-c2", ".example", ".net", "/beacon"]
    return "".join(partes)

def main():
    print("Agente didatico da Panthera Quarentena. Inofensivo.")

if __name__ == "__main__":
    main()
'''
open("agente_fonte.py", "w", encoding="utf-8").write(fonte)
print("agente_fonte.py gerado")
