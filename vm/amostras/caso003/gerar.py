#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 003: analise de IMPORTS. ELF que importa funcoes de rede e de arquivo
# (sem chamar nada perigoso), para o aluno prever o comportamento so pela tabela
# de imports. INOFENSIVO.
fonte = '''// Amostra 003 (analise de imports) da Panthera Quarentena - INOFENSIVA.
// Referencia os simbolos para forcar os imports, sem chamar nada.
#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>
void *refs[] = { (void*)socket, (void*)connect, (void*)send, (void*)recv, (void*)fopen, (void*)fwrite };
int main(void) { (void)refs; puts("Amostra 003 (analise de imports). Inofensiva."); return 0; }
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c gerada (imports de rede + arquivo)")
