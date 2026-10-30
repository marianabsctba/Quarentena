#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 025 (avancado): INDICADORES de injecao de processo, so-deteccao. INOFENSIVO.
# process_vm_writev e o syscall que ESCREVE na memoria de OUTRO processo (a base
# da injecao no Linux). Aqui o "alvo" e o PROPRIO pid (getpid): a amostra copia
# bytes dentro de si mesma, entao nada e injetado em ninguem. O aluno detecta a
# CAPACIDADE pelo import (readelf) e ve, no Ghidra, que o alvo e o proprio processo.
fonte = '''// Amostra 025 (indicadores de injecao) da Panthera Quarentena - INOFENSIVA.
// Usa process_vm_writev contra o PROPRIO pid: demonstra o primitivo sem injetar
// em ninguem. Nao anexa a outro processo, nao escreve fora de si.
#define _GNU_SOURCE
#include <stdio.h>
#include <sys/uio.h>
#include <unistd.h>

int main(void){
    char origem[16] = "didatico";
    char destino[16] = {0};
    struct iovec local  = { origem,  8 };
    struct iovec remoto = { destino, 8 };   /* "remoto" = este mesmo processo */
    /* process_vm_writev: escrita em memoria de processo. Alvo = getpid() = eu. */
    process_vm_writev(getpid(), &local, 1, &remoto, 1, 0);
    printf("Amostra 025 (indicadores de injecao): destino=%s. Inofensiva.\\n", destino);
    return 0;
}
'''
open("fonte.c", "w", encoding="utf-8").write(fonte)
print("fonte.c 024 gerada (process_vm_writev contra o proprio pid).")
