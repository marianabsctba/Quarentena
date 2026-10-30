#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 012 (avancado): INDICADORES de ransomware, so-deteccao. INOFENSIVO.
# A amostra NAO cifra, NAO renomeia e NAO apaga nada. Ela apenas CARREGA as
# strings tipicas de um ransomware (nota de resgate, extensao, nome do arquivo
# de nota) pra o aluno aprender a reconhecer a familia pela analise estatica.
# main() so imprime um aviso.
fonte = '''// Amostra 012 (indicadores de ransomware) da Panthera Quarentena - INOFENSIVA.
// Nada e cifrado, renomeado ou apagado. So guarda strings indicadoras.
#include <stdio.h>
static const char nota[] =
    "SEUS ARQUIVOS FORAM TRANCADOS. Para recuperar, siga as instrucoes.";
static const char ext[] = ".trancado";             /* extensao aposta nos arquivos */
static const char nota_arq[] = "COMO_RECUPERAR.txt"; /* nome do arquivo de resgate */
int main(void){
    (void)nota; (void)ext; (void)nota_arq;
    puts("Amostra 012 (indicadores de ransomware). Inofensiva: nada foi cifrado.");
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c 021 gerada (apenas indicadores, sem comportamento destrutivo).")
