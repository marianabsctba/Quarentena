#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 030 (mestre): CAPSTONE. INOFENSIVO.
# Junta varias tecnicas vistas no curso num binario so: anti-debug (ptrace),
# C2 escondido em base64 e uma string-marca unica. O aluno faz a analise
# completa e escolhe uma assinatura estavel pra escrever uma regra YARA.
import base64
C2 = "http://capstone-c2.example.org/z"
C2_B64 = base64.b64encode(C2.encode()).decode()
MARCA = "PANTHERA_CAPSTONE_v1"
fonte = '''// Amostra 030 (capstone) da Panthera Quarentena - INOFENSIVA.
// Combina: anti-debug (ptrace), C2 em base64 e uma marca unica. Nao conecta,
// nao persiste; o ptrace(TRACEME) so serve de anti-debug didatico.
#include <stdio.h>
#include <sys/ptrace.h>
static const char marca[]  = "%s";   /* assinatura estavel pra YARA */
static const char c2_b64[] = "%s";   /* C2 escondido em base64 */
int main(void){
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {  /* anti-debug */
        puts("ambiente de depuracao detectado; encerrando.");
        return 0;
    }
    (void)marca; (void)c2_b64;
    puts("Amostra 030 (capstone). Inofensiva.");
    return 0;
}
''' % (MARCA, C2_B64)
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c 030 gerada. marca=%s c2=%s base64=%s" % (MARCA, C2, C2_B64))
