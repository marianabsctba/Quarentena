#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor local do Quarentena (roda DENTRO da VM).

Serve o front-end 3D e expõe uma API que:
  - roda ferramentas de linha de comando REAIS sobre a amostra do caso atual
    (strings, readelf, objdump, xxd, file, sha256sum, strace, cat) e devolve a
    saída para o 3D mostrar;
  - abre as ferramentas GUI REAIS (Ghidra, terminal, YARA...);
  - confere as respostas que o aluno achou usando as ferramentas de verdade.

Só escuta em 127.0.0.1. Só executa comandos de uma lista fixa (allowlist);
nunca roda comando vindo do navegador. As amostras são didáticas e inofensivas.
"""
import json
import os
import shutil
import subprocess
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import curso

BASE = os.path.dirname(os.path.abspath(__file__))        # vm/guia
VM = os.path.dirname(BASE)                                # vm
WEB = os.path.join(BASE, "web")
AMOSTRAS = os.path.join(VM, "amostras")

PORT = 8777
MAX_SAIDA = 24000

# Ferramentas de texto: a saída aparece no 3D. Cada uma recebe o caminho da amostra.
EXEC = {
    "hex":     lambda s: ["xxd", s],
    "strings": lambda s: ["strings", s],
    "elf":     lambda s: ["readelf", "-hSsW", s],
    "disasm":  lambda s: ["objdump", "-d", "-M", "intel", s],
    "strace":  lambda s: ["strace", "-f", "-e", "trace=file,network", s, "--arm"],
    "cat":     lambda s: ["cat", s],
    "tshark":  lambda s: ["tshark", "-r", s],
}
# "triagem" roda file + sha256sum (tratado à parte).

# Ferramentas GUI: tenta cada candidato até achar um instalado.
ABRIR = {
    "ghidra":   [["ghidraRun"], ["ghidra"]],
    "xor":      [["xdg-open", os.path.join(WEB, "cyberchef", "index.html")], ["cyberchef"],
                 ["xdg-open", "https://gchq.github.io/CyberChef/"]],
    "yara":     [["x-terminal-emulator"], ["gnome-terminal"], ["konsole"], ["xterm"]],
    "terminal": [["x-terminal-emulator"], ["gnome-terminal"], ["konsole"], ["xterm"]],
}


def amostra_de(caso_id):
    """Retorna (diretorio, caminho_da_amostra, caminho_do_build) do caso."""
    c = curso.caso_por_id(caso_id)
    if not c:
        return None, None, None
    d = os.path.join(AMOSTRAS, c["dir"])
    return d, os.path.join(d, c["arquivo"]), os.path.join(d, "build.sh")


def sh(cmd, cwd=None, timeout=60):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "") + (("\n[stderr]\n" + p.stderr) if p.stderr else "")
        return True, out[:MAX_SAIDA]
    except FileNotFoundError:
        return False, "ferramenta não instalada nesta máquina: " + cmd[0]
    except subprocess.TimeoutExpired:
        return False, "a ferramenta demorou demais e foi interrompida."
    except Exception as e:
        return False, "erro ao rodar: " + str(e)


def garantir_amostra(caso_id):
    d, sample, build = amostra_de(caso_id)
    if sample is None:
        return False
    if not os.path.exists(sample) and os.path.exists(build):
        sh(["bash", build], cwd=d, timeout=120)
    return os.path.exists(sample)


def rodar_exec(caso_id, tool):
    d, sample, _ = amostra_de(caso_id)
    if sample is None:
        return False, "caso desconhecido."
    if not garantir_amostra(caso_id):
        return False, "a amostra ainda não foi compilada (rode bash build.sh)."
    if tool == "triagem":
        ok1, t = sh(["file", sample])
        ok2, h = sh(["sha256sum", sample])
        return (ok1 or ok2), (t + "\n" + h)
    if tool == "entropia":
        import math, collections
        data = open(sample, "rb").read()
        if not data:
            return True, "arquivo vazio."
        c = collections.Counter(data); n = len(data)
        e = -sum(v / n * math.log2(v / n) for v in c.values())
        return True, ("Entropia de Shannon: %.3f de 8.000  (%d bytes)\n"
                      "Perto de 8 = bytes aleatorios (empacotado, comprimido ou cifrado)." % (e, n))
    if tool in EXEC:
        return sh(EXEC[tool](sample))
    return False, "essa ferramenta não roda em modo texto; use o botão de abrir."


def abrir_gui(caso_id, tool):
    d, _, _ = amostra_de(caso_id)
    for cand in ABRIR.get(tool, []):
        # pula um "xdg-open <arquivo local>" quando o arquivo ainda nao existe
        # (ex: CyberChef offline nao baixado): cai pro proximo candidato.
        if len(cand) > 1 and cand[0] == "xdg-open" \
           and not cand[1].startswith(("http://", "https://")) \
           and not os.path.exists(cand[1]):
            continue
        if shutil.which(cand[0]):
            try:
                subprocess.Popen(cand, cwd=d, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
                return True, "abrindo: " + " ".join(cand)
            except Exception as e:
                return False, "falhou ao abrir " + cand[0] + ": " + str(e)
    sugestao = ABRIR.get(tool, [["(nenhum)"]])[0][0]
    return False, "não achei '" + sugestao + "' instalado. Na VM final ele estará; aqui pode faltar."


def conferir(caso_id, passo_id, resposta):
    p = curso.achar_passo(caso_id, passo_id)
    if not p:
        return False, "passo desconhecido."
    dado = (resposta or "").strip()
    if p.get("resposta_tipo") == "sha256":
        _, sample, _ = amostra_de(caso_id)
        if not garantir_amostra(caso_id):
            return False, "amostra não compilada."
        real = hashlib.sha256(open(sample, "rb").read()).hexdigest()
        if dado.lower() == real:
            return True, p["sucesso"]
        return False, "Não bate com o hash real da amostra. Rode 'sha256sum' e cole exatamente."
    low = dado.lower()
    ok = low == p["resposta"].lower()
    if not ok and p.get("contem"):
        ok = p["contem"].lower() in low
    if ok:
        return True, p["sucesso"]
    return False, "Ainda não. Use a ferramenta indicada e olhe com calma."


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8" if ctype.startswith(("text", "application")) else ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/curso":
            return self._send(200, curso.curso_dict())
        return self._servir_estatico(path)

    def do_POST(self):
        path = self.path.split("?")[0]
        b = self._body()
        caso = b.get("caso", "")
        if path == "/api/exec":
            ok, out = rodar_exec(caso, b.get("tool", ""))
            return self._send(200, {"ok": ok, "saida": out})
        if path == "/api/abrir":
            ok, msg = abrir_gui(caso, b.get("tool", ""))
            return self._send(200, {"ok": ok, "msg": msg})
        if path == "/api/responder":
            ok, msg = conferir(caso, b.get("passo", ""), b.get("resposta", ""))
            return self._send(200, {"ok": ok, "msg": msg})
        return self._send(404, {"erro": "rota desconhecida"})

    def _servir_estatico(self, path):
        if path in ("/", ""):
            path = "/index.html"
        alvo = os.path.normpath(os.path.join(WEB, path.lstrip("/")))
        if not alvo.startswith(WEB) or not os.path.isfile(alvo):
            return self._send(404, "não encontrado", "text/plain")
        tipos = {".html": "text/html", ".js": "application/javascript", ".css": "text/css",
                 ".webp": "image/webp", ".png": "image/png", ".svg": "image/svg+xml", ".json": "application/json"}
        ext = os.path.splitext(alvo)[1].lower()
        with open(alvo, "rb") as f:
            self._send(200, f.read(), tipos.get(ext, "application/octet-stream"))


def main():
    for c in curso.CASOS:
        garantir_amostra(c["id"])
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print("Quarentena rodando em http://127.0.0.1:%d" % PORT)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
