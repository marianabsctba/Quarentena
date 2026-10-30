#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o site estatico do Pages em pages/saida/site (a imagem ja esta em fs/).

Reaproveita o curso e o front da VM. Troca os passos do Ghidra, que nao roda no
navegador, por outras ferramentas e ajusta as falas que so faziam sentido na VM.
"""
import hashlib
import json
import os
import shutil
import sys
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SITE = os.path.join(AQUI, "saida", "site")
WEB = os.path.join(RAIZ, "vm", "guia", "web")
NODE = os.path.join(AQUI, "node_modules")
BIOS = "https://raw.githubusercontent.com/copy/v86/cc37f35c43bf14865d74ad76879ecf9410f69eb1/bios/"

sys.path.insert(0, os.path.join(RAIZ, "vm", "guia"))
import curso  # noqa: E402

INTRO_FALAS = {
    "Essa VM é isolada: sem rede de verdade, com snapshot salvo. Se bagunçar, a gente volta o snapshot e finge que nada aconteceu. Como na vida.":
    "Essa VM roda dentro da aba do seu navegador, sem rede nenhuma. Se bagunçar, recarrega a página: volta tudo ao zero e a gente finge que nada aconteceu. Como na vida.",
}
# O Ghidra nao roda no navegador: cada passo dele volta com a ferramenta que
# responde a mesma pergunta aqui, conferida nas amostras de 32 bits.
SEM_GHIDRA = {
    ("caso001", "p6"): {
        "tool": "terminal",
        "instr": "O Ghidra fica na VM, mas dá pra achar a chave na unha. A decrypt_strings faz XOR com o símbolo KEY. No Terminal, ache o endereço dele com objdump -t fatura_outubro | grep KEY e leia a seção com objdump -s -j .rodata fatura_outubro. Qual o valor (em hex) nesse endereço?",
        "dica": "O KEY está no começo do .rodata: é o primeiro byte da primeira linha do dump.",
        "sucesso": "0x2A. Achou a chave lendo o binário de verdade. Isso é engenharia reversa: o programa tentou esconder, você leu assim mesmo.",
    },
    ("caso003", "p4"): {"tool": "elf"},
    ("caso019", "p3"): {
        "tool": "strings",
        "instr": "Dentro do /proc/self/status tem um campo que vale 0 quando não há debugger e vira o PID do depurador quando tem um anexado. O nome dele precisa estar no binário pra ser comparado. Ache no Strings.",
        "dica": "Procure um texto terminado em dois-pontos, com 'Pid' no nome.",
    },
    ("caso020", "p5"): {
        "tool": "disasm",
        "instr": "Abra o Desmontador. Sem nomes, procure o laço de decodificação (um xor entre registradores). Logo antes dele, a chave é indexada: o compilador trocou 'i % N' por um 'and' com N-1. De quantos bytes é a chave?",
        "dica": "Procure 'and edx,0x3' perto do xor. And com 3 é o mesmo que resto da divisão por 4.",
    },
    ("caso025", "p3"): {
        "tool": "disasm",
        "instr": "No Desmontador, ache a chamada a process_vm_writev: o primeiro argumento é o PID alvo. Nesta amostra didática, de onde vem esse PID (qual função é chamada logo antes)?",
    },
}
# (caso, passo, campo): texto que nao batia com a saida real no Linux do navegador.
AJUSTES = {
    # Sob strace o ptrace(TRACEME) falha: o anti-debug dispara e o arquivo nunca e criado.
    ("caso001", "p8", "tool"): "terminal",
    ("caso001", "p8", "instr"): "Análise estática conta a intenção; a dinâmica confirma. Na Sandbox (strace) ela percebe o rastreador e encerra: é o anti-debug que você achou. Então rode sem coleira, no Terminal: ./fatura_outubro --arm e depois ls /tmp.",
    ("caso001", "p8", "dica"): "A amostra é inofensiva. Rode ./fatura_outubro --arm no Terminal e liste o /tmp. Compare com a Sandbox, onde ela desiste antes de criar qualquer coisa.",
    # Aqui tambem o ptrace dispara primeiro: o strace nao chega a mostrar o product_name.
    ("caso020", "p7", "instr"): "Rode na Sandbox (strace) em modo --arm e observe: ele encerra calado, sem tocar em nada. Além do ptrace, ele carrega a checagem do product_name, feita pra se recusar a agir dentro de uma VM.",
    ("caso020", "p7", "dica"): "O product_name existe pra ele perceber que está numa VM. O nome da técnica combina 'anti' com onde você está rodando.",
}
TROCAS = [("Abra o Desmontador (ou Ghidra).", "Abra o Desmontador."),
          ("O algoritmo (visível no Ghidra) é", "O algoritmo (visível no Desmontador) é"),
          # A musl de 32 bits chama open, nao openat.
          ("open/openat", "open"), ("openat", "open")]
HTML_TROCAS = [("rede: FakeNet", "rede: desligada"), ("snapshot: salvo", "recarregar: volta ao zero"),
               ("Não consegui falar com o servidor local. Rode: python3 servidor.py",
                "Não consegui falar com o Linux do laboratório. Recarregue a página."),
               ("Não consegui falar com o servidor local. Ele está rodando? (python3 servidor.py)",
                "Não consegui falar com o Linux do laboratório. Recarregue a página.")]
# Ferramenta que o passo ajustado passa a pedir e que o caso nao listava.
TOOLS_EXTRAS = {"caso001": ["terminal"], "caso025": ["disasm"]}


def hashes():
    r = {}
    with open(os.path.join(SITE, "fs", "sha256.txt")) as f:
        for linha in f:
            h, nome = linha.split()
            r[nome.lstrip("./")] = h
    return r


def montar_curso():
    sha = hashes()
    casos = []
    for c in curso.CASOS:
        passos = []
        for p in c["passos"]:
            p = dict(p, **SEM_GHIDRA.get((c["id"], p["id"]), {}))
            assert p["tool"] != "ghidra", (c["id"], p["id"])
            for campo in ("instr", "dica", "sucesso"):
                for de, para in TROCAS:
                    p[campo] = p[campo].replace(de, para)
            for campo in ("tool", "instr", "dica", "sucesso"):
                novo = AJUSTES.get((c["id"], p["id"], campo))
                if novo:
                    p[campo] = novo
            passos.append(p)
        tools = [dict(curso.TOOLS[t], id=t) for t in c["tools"] + TOOLS_EXTRAS.get(c["id"], []) if t != "ghidra"]
        casos.append({"id": c["id"], "nome": c["nome"], "nivel": c["nivel"],
                      "arquivo": c["arquivo"], "origem": c["origem"],
                      "sha256": sha[c["dir"] + "/" + c["arquivo"]],
                      "tools": tools, "passos": passos})
    intro = dict(curso.INTRO)
    intro["falas"] = [INTRO_FALAS.get(f, f) for f in intro["falas"]]
    return {"intro": intro, "casos": casos}


def copiar(origem, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copyfile(origem, destino)


def main():
    with open(os.path.join(SITE, "curso.json"), "w", encoding="utf-8") as f:
        json.dump(montar_curso(), f, ensure_ascii=False)

    vendor = os.path.join(SITE, "vendor")
    copiar(os.path.join(WEB, "panthera.webp"), os.path.join(SITE, "panthera.webp"))
    copiar(os.path.join(WEB, "vendor", "three.min.js"), os.path.join(vendor, "three.min.js"))
    for origem, nome in [("v86/build/libv86.js", "libv86.js"), ("v86/build/v86.wasm", "v86.wasm"),
                         ("@xterm/xterm/lib/xterm.js", "xterm.js"), ("@xterm/xterm/css/xterm.css", "xterm.css"),
                         ("@xterm/addon-fit/lib/addon-fit.js", "addon-fit.js")]:
        copiar(os.path.join(NODE, *origem.split("/")), os.path.join(vendor, nome))
    for b in ("seabios.bin", "vgabios.bin"):
        destino = os.path.join(vendor, b)
        if not os.path.exists(destino):
            urllib.request.urlretrieve(BIOS + b, destino)

    with open(os.path.join(WEB, "index.html"), encoding="utf-8") as f:
        html = f.read()
    extras = ('<link rel="stylesheet" href="vendor/xterm.css">\n'
              '<script src="vendor/libv86.js"></script>\n'
              '<script src="vendor/xterm.js"></script>\n'
              '<script src="vendor/addon-fit.js"></script>\n'
              '<script src="navegador.js"></script>\n')
    marca = '<script src="vendor/three.min.js"></script>\n'
    if marca not in html:
        html = html.replace(marca.strip(), marca.strip() + "\n")
    for de, para in HTML_TROCAS:
        html = html.replace(de, para)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html.replace(marca, marca + extras, 1))

    # O estado guarda a arvore de arquivos: estado e imagem de versoes diferentes
    # travam o Linux. A versao no nome impede que o cache misture os dois.
    with open(os.path.join(SITE, "fs", "fs.json"), "rb") as f:
        versao = hashlib.sha256(f.read()).hexdigest()[:12]
    for nome in ("sw.js", "navegador.js"):
        with open(os.path.join(AQUI, "web", nome), encoding="utf-8") as f:
            texto = f.read().replace("__VERSAO__", versao)
        with open(os.path.join(SITE, nome), "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
    with open(os.path.join(AQUI, "saida", "versao.txt"), "w") as f:
        f.write(versao)
    open(os.path.join(SITE, ".nojekyll"), "w").close()
    print("ok:", SITE)


if __name__ == "__main__":
    main()
