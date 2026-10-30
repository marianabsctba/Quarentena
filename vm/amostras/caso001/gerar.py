#!/usr/bin/env python3
# Gera a fonte C da amostra didatica do Caso 001 (Panthera Quarentena - Quarentena).
#
# A amostra e INOFENSIVA: nao conecta em lugar nenhum, nao persiste de verdade,
# nao ataca nada. Ela apenas carrega tracos REAIS de engenharia reversa para
# treino (uma URL ofuscada com XOR, uma checagem de anti-debug com ptrace,
# simbolos legiveis), de modo que as ferramentas reais (strings, readelf,
# radare2, Ghidra) mostrem resultado de verdade ao analisa-la.

C2 = "http://atualizador-seguro.ddns.net/gate.php"
KEY = 0x2A

enc = bytes(b ^ KEY for b in C2.encode())
arr = ", ".join("0x%02x" % b for b in enc)

fonte = '''// Amostra didatica da Panthera Quarentena - Caso 001 - INOFENSIVA.
// Gerada por gerar.py. Nao faz nada malicioso: simula tecnicas reais
// (string ofuscada com XOR, checagem anti-debug, simbolos) so para treino.
#include <stdio.h>
#include <string.h>
#include <sys/ptrace.h>

/* URL do "C2" ofuscada com XOR 0x%02X (nao aparece em texto claro) */
static unsigned char enc_c2[] = { %s };
static const unsigned char KEY = 0x%02X;

void decrypt_strings(char *out, const unsigned char *in, int n) {
    int i;
    for (i = 0; i < n; i++) out[i] = in[i] ^ KEY;
    out[n] = 0;
}

/* Tecnica real de anti-debug: se um debugger ja esta anexado, PTRACE_TRACEME falha. */
int anti_debug(void) {
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) return 1;
    return 0;
}

/* INOFENSIVO: apenas registra a intencao, nunca conecta de verdade. */
void connect_c2(const char *url) {
    fprintf(stderr, "[amostra] contataria o C2: %%s\\n", url);
}

/* INOFENSIVO: marcador didatico, nao e persistencia de verdade. */
void fake_persistence(void) {
    FILE *f = fopen("/tmp/panthera_persistence.txt", "w");
    if (f) { fprintf(f, "marcador didatico de persistencia (inofensivo)\\n"); fclose(f); }
}

int main(int argc, char **argv) {
    char url[128];
    decrypt_strings(url, enc_c2, sizeof(enc_c2));
    if (argc > 1 && strcmp(argv[1], "--arm") == 0) {
        if (anti_debug()) { puts("ambiente de analise detectado, encerrando."); return 0; }
        fake_persistence();
        connect_c2(url);
        puts("amostra 'armada' em modo didatico (nada perigoso aconteceu).");
    } else {
        puts("Amostra didatica da Panthera Quarentena (Caso 001). Inofensiva.");
        puts("Analise-me com as ferramentas: hex, strings, readelf, radare2/Ghidra.");
    }
    return 0;
}
''' % (KEY, arr, KEY)

with open("fonte.c", "w", encoding="utf-8") as f:
    f.write(fonte)

print("fonte.c gerada. C2 ofuscado com chave 0x%02X, %d bytes." % (KEY, len(enc)))
