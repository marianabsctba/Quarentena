# Currículo do Quarentena (30 casos de referência)

Meta: 30 casos, cada um com uma técnica distinta e genuína de engenharia
reversa de malware, do iniciante ao mestre. Toda amostra é benigna (compilada de
fonte, nunca malware real) e testada com as ferramentas de verdade.

Status: `PRONTO` = implementado e testado. `planejado` = na fila.
`na VM` = depende de ferramenta que só existe na VM final (ex: UPX), então a
amostra é construída/testada no provisionamento. `só-detec.` = tema sensível
(ransomware, injeção): a amostra NÃO implementa a
capacidade ofensiva; ela só exibe os INDICADORES (nota de resgate, chamada de
injeção...) pro aluno aprender a DETECTAR, nunca a
construir. Nada de código de ataque funcional no curso.

| #   | Nível | Caso / técnica central | Ferramentas | MITRE | Status |
|-----|-------|------------------------|-------------|-------|--------|
| 001 | iniciante | ELF backdoor: assinatura, hex, strings, imports, XOR 1b | hex, strings, objdump | T1622 | PRONTO |
| 002 | iniciante | Hexadecimal embutido no binário: disfarce, não cadeado | strings, xxd | T1140 | PRONTO |
| 003 | iniciante | Análise de imports: prever comportamento sem rodar | readelf | varias | PRONTO |
| 004 | iniciante | Entropia: detecção de empacotamento | entropia, readelf | T1027.002 | PRONTO |
| 005 | intermediário | Reverse shell em bash (/dev/tcp) | cat | T1059.004 | PRONTO |
| 006 | intermediário | Payload comprimido (gzip) embutido: descomprimir | file, xxd, terminal | T1027 | PRONTO |
| 007 | intermediário | Overlay: dados depois do fim do ELF | readelf, strings, terminal | T1027.009 | PRONTO |
| 008 | intermediário | Script cryptominer: base64 duplo, pool, cron | cat, terminal | T1496, T1053.003 | PRONTO |
| 009 | intermediário | Bytecode Python: ler um .pyc sem o fonte | file, strings, dis | T1059.006 | PRONTO |
| 010 | intermediário | Credential stealer: /etc/passwd e chaves SSH | strace, objdump | T1552.001 | PRONTO |
| 011 | intermediário | Disfarce de processo: prctl(PR_SET_NAME) | readelf, strings, strace | T1036 | PRONTO |
| 012 | intermediário | Indicadores de ransomware (nota, extensão, extorsão) | strings | T1486 | só-detec. |
| 013 | intermediário | Trava de execução: só age no host alvo | strace, strings, terminal | T1480 | PRONTO |
| 014 | intermediário | Anti-sandbox por tempo (sleep) e nº de CPUs | objdump, strace | T1497.003 | PRONTO |
| 015 | intermediário | Rede (pcap): C2 beacon e exfiltração em cookie | tshark, terminal | T1071, T1041 | PRONTO |
| 016 | intermediário | DNS tunneling (pcap): exfiltração por consultas DNS | tshark | T1048, T1071.004 | PRONTO |
| 017 | intermediário | DGA: reverter e prever domínios | cat, terminal | T1568.002 | PRONTO |
| 018 | avançado | Stack strings: estática cega, dinâmica revela | disasm, strace | T1027 | PRONTO |
| 019 | avançado | Anti-debug via /proc/self/status (TracerPid) | strace, objdump | T1622 | PRONTO |
| 020 | avançado | ELF stripped: XOR multi-byte, anti-debug, anti-VM | readelf, objdump | T1497 | PRONTO |
| 021 | avançado | Decriptação de strings estilo RC4 | objdump, python | T1027 | PRONTO |
| 022 | avançado | Packing com UPX: reconhecer "UPX!" e desempacotar (upx -d) | strings, terminal | T1027.002 | na VM |
| 023 | avançado | ELF auto-decodificante (unpacking manual em memória) | strace, objdump | T1027.002 | PRONTO |
| 024 | avançado | Construtor: código e anti-debug antes da main (.init_array) | objdump, readelf, strace | T1622 | PRONTO |
| 025 | avançado | Indicadores de injeção (process_vm_writev no proprio pid) | readelf, objdump | T1055 | só-detec. |
| 026 | avançado | Shellcode isolado: desmontar bytes crus (-b binary) | xxd, objdump | T1055 | PRONTO |
| 027 | mestre | API hashing (djb2): reverter o hash pro nome da API | objdump, terminal | T1027.007 | PRONTO |
| 028 | mestre | C2 cifrado no pcap: XOR de 1 byte, decifrar o comando | tshark, terminal | T1573 | PRONTO |
| 029 | mestre | Reversão de protocolo próprio de C2 (magic+opcode+len) | tshark, terminal | T1095 | PRONTO |
| 030 | mestre | Capstone: anti-debug + C2 base64 + regra YARA | todas, YARA | T1622, varias | PRONTO |


Progresso: **30 de 30 escritos**, do iniciante ao mestre (001-004 iniciante,
005-017 intermediário, 018-026 avançado, 027-030 mestre). Cada caso ensina uma
técnica que os outros não ensinam.
