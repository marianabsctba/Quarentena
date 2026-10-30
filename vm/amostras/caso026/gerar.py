#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 026 (avancado): SHELLCODE isolado (bytes crus). INOFENSIVO.
# Nao e um ELF: e so um punhado de bytes de codigo de maquina, sem cabecalho,
# sem secoes. O 'file' nao reconhece. O aluno precisa desmontar como codigo cru
# (objdump -D -b binary -m i386:x86-64) pra ler as instrucoes. O codigo aqui e
# aritmetica pura, SEM syscall: mov eax,0x1337; add eax,7; ret. Nao faz nada.
code = bytes([
    0xB8, 0x37, 0x13, 0x00, 0x00,   # mov    eax, 0x1337
    0x83, 0xC0, 0x07,               # add    eax, 7
    0xC3,                           # ret
])
open("shellcode.bin", "wb").write(code)
print("shellcode.bin gerado (%d bytes): %s" % (len(code), code.hex()))
