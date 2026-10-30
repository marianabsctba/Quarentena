# Caso 001 - amostra didática

Amostra de treino do Quarentena. **É inofensiva**: não conecta em lugar nenhum,
não persiste de verdade e não ataca nada. Ela só carrega traços reais de
engenharia reversa para o estudante analisar com as ferramentas de verdade.

## O que ela tem (para treino)

- Uma URL de "C2" **ofuscada com XOR** (chave `0x2A`), que não aparece em texto
  claro (o `strings` não revela, é preciso decodificar).
- Uma checagem de **anti-debug** real com `ptrace(PTRACE_TRACEME)`.
- Símbolos legíveis (`connect_c2`, `decrypt_strings`, `anti_debug`,
  `fake_persistence`, `main`) para ler no Ghidra / radare2.
- Um marcador de "persistência" que só escreve um arquivo de aviso em `/tmp`
  (nada de persistência de verdade).

## Como gerar e compilar

```bash
bash build.sh
```

Precisa de `python3` e `gcc` (já vêm no Ubuntu/REMnux). O build gera `fonte.c`
e compila o ELF `fatura_outubro` (sem strip, sem PIE, para ficar legível na
análise). Os dois são saídas de build e não entram no versionamento.

## Rodar (opcional, inofensivo)

```bash
./fatura_outubro          # imprime um aviso e sai
./fatura_outubro --arm    # modo didático: escreve o marcador em /tmp e sai
```
