// Faz no navegador o papel do servidor.py: liga um Linux real na aba (v86), roda
// as ferramentas nele pela segunda porta serial e confere as respostas.
window.QuarentenaNavegador = (function () {
  "use strict";
  var CURSO = null, emu = null, seq = 0, buf = "", esperando = {};
  var aviso = null, inicio = 0, ligado = null, fila = Promise.resolve();
  var term = null, encaixe = null, termEl = null, casoTerm = null;
  var LIMITE_MS = 120000;

  function caso(id) { return CURSO.casos.filter(function (c) { return c.id === id; })[0]; }
  function status(txt, ok) {
    if (!aviso) {
      aviso = document.createElement("div");
      aviso.style.cssText = "position:fixed;right:12px;bottom:64px;z-index:50;padding:7px 12px;border-radius:6px;" +
        "background:#120a10;border:1px solid #ff2f9a;color:#ffc4e3;font:12px monospace";
      document.body.appendChild(aviso);
    }
    aviso.textContent = txt;
    if (ok) setTimeout(function () { aviso.style.display = "none"; }, 4000);
  }

  function linhaAgente(id, c, arquivo, tool) {
    var txt = [id, c, arquivo, tool].join(" ") + "\n", b = new Uint8Array(txt.length);
    for (var i = 0; i < txt.length; i++) b[i] = txt.charCodeAt(i);
    emu.serial_send_bytes(1, b);
  }

  function cacheAtivo() {
    if (!navigator.serviceWorker) return Promise.resolve();
    return navigator.serviceWorker.register("sw.js").then(function () {
      return navigator.serviceWorker.ready;
    }).catch(function () {});
  }

  function ligar() {
    if (ligado) return ligado;
    inicio = performance.now();
    ligado = cacheAtivo().then(function () { return new Promise(function (resolve) {
      var relogio = setInterval(function () {
        status("Ligando o Linux do laboratório... " + Math.round((performance.now() - inicio) / 1000) + "s");
      }, 1000);
      emu = new V86({
        wasm_path: "vendor/v86.wasm",
        memory_size: 256 * 1024 * 1024,
        vga_memory_size: 2 * 1024 * 1024,
        bios: { url: "vendor/seabios.bin" },
        vga_bios: { url: "vendor/vgabios.bin" },
        filesystem: { baseurl: "fs/flat/", basefs: "fs/fs.json?v=__VERSAO__" },
        initial_state: { url: "estado-__VERSAO__.bin.zst" },
        uart1: true,
        disable_keyboard: true,
        disable_mouse: true,
        autostart: true
      });
      emu.add_listener("download-progress", function (e) {
        if (e.file_name.indexOf("estado") < 0 || !e.total) return;
        clearInterval(relogio);
        status("Baixando o laboratório... " + Math.round(e.loaded / e.total * 100) + "%");
      });
      emu.add_listener("serial1-output-byte", function (b) {
        if (b !== 10) { buf += String.fromCharCode(b); return; }
        var m = /FIM (\d+)/.exec(buf); buf = "";
        if (m && esperando[m[1]]) { esperando[m[1]](); delete esperando[m[1]]; }
      });
      emu.add_listener("serial0-output-byte", function (b) {
        if (term) term.write(new Uint8Array([b]));
      });
      // O agente responde quando o boot acaba; ate la, os pedidos ficam sem resposta.
      var pingId = String(++seq);
      esperando[pingId] = function () {
        clearInterval(ping); clearInterval(relogio);
        status("Linux pronto em " + Math.round((performance.now() - inicio) / 1000) + "s", true);
        resolve();
      };
      var ping = setInterval(function () {
        if (emu.is_running()) linhaAgente(pingId, "-", "-", "-");
      }, 1500);
    }); });
    return ligado;
  }

  function exec(c, tool) {
    // Um pedido por vez: todos gravam a saida no mesmo arquivo.
    var r = fila.then(ligar).then(function () {
      return new Promise(function (ok) {
        var id = String(++seq);
        esperando[id] = ok;
        linhaAgente(id, c.id, c.arquivo, tool);
      });
    }).then(function () {
      return emu.read_file("/var/lib/quarentena/saida");
    }).then(function (bytes) {
      return { ok: true, saida: new TextDecoder().decode(bytes) };
    });
    fila = r.catch(function () {});
    return Promise.race([r, new Promise(function (ok) {
      setTimeout(function () {
        ok({ ok: false, saida: "O Linux do laboratório não respondeu. Recarregue a página." });
      }, LIMITE_MS);
    })]);
  }

  // Acento, maiuscula e espaco nao mudam a resposta: nao, NÃO, 1f8b, 1f 8b.
  function normalizar(t) {
    return t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, "").toLowerCase();
  }

  function conferir(c, passoId, resposta) {
    var p = c.passos.filter(function (x) { return x.id === passoId; })[0];
    if (!p) return { ok: false, msg: "passo desconhecido." };
    var dado = normalizar(resposta || "");
    if (p.resposta_tipo === "sha256") {
      return dado === c.sha256 ? { ok: true, msg: p.sucesso }
        : { ok: false, msg: "Não bate com o hash real da amostra. Rode 'sha256sum' e cole exatamente." };
    }
    var contem = [].concat(p.contem || []);
    var ok = dado === normalizar(p.resposta) || contem.some(function (x) { return dado.indexOf(normalizar(x)) >= 0; });
    return ok ? { ok: true, msg: p.sucesso } : { ok: false, msg: "Ainda não. Use a ferramenta indicada e olhe com calma." };
  }

  function api(path, body) {
    if (path === "/api/curso") {
      return fetch("curso.json").then(function (r) { return r.json(); }).then(function (c) {
        CURSO = c; ligar(); return c;
      });
    }
    var c = caso(body.caso);
    if (path === "/api/exec") return exec(c, body.tool);
    if (path === "/api/responder") return Promise.resolve(conferir(c, body.passo, body.resposta));
    return Promise.reject(new Error("rota desconhecida: " + path));
  }

  function abrirTerminal(c, area) {
    if (!term) {
      termEl = document.createElement("div");
      termEl.style.cssText = "height:100%;min-height:380px";
      term = new Terminal({ fontFamily: "monospace", fontSize: 13, convertEol: false,
        theme: { background: "#08060a", foreground: "#ffd9ec", cursor: "#ff2f9a" } });
      encaixe = new FitAddon.FitAddon();
      term.loadAddon(encaixe);
      term.open(termEl);
      term.onData(function (d) { if (emu) emu.serial0_send(d); });
      window.addEventListener("resize", function () { if (termEl.isConnected) encaixe.fit(); });
    }
    area.innerHTML = "";
    area.appendChild(termEl);
    encaixe.fit();
    term.focus();
    ligar().then(function () {
      if (casoTerm !== c.id) {
        casoTerm = c.id;
        emu.serial0_send("\ncd /casos/" + c.id + " && clear && ls\n");
      }
    });
  }

  function abrirCyberChef(c, area) {
    var p = c.passos.filter(function (x) { return x.cyberchef; })[0];
    var site = "<a style='color:#ff79c0' target='_blank' rel='noopener' href='https://gchq.github.io/CyberChef/'>Abrir o CyberChef</a>";
    var caixa = document.createElement("div");
    caixa.style.cssText = "padding:14px;font-size:14px;line-height:1.6;color:#e8dfe4";
    if (!p) {
      caixa.innerHTML = "O <b>CyberChef</b> decodifica dados: você cola no Input, escolhe a receita e lê o resultado no Output. " +
        "O veterano diz o que colar em cada passo.<br><br>" + site;
      area.innerHTML = ""; area.appendChild(caixa);
      return;
    }
    var cc = p.cyberchef, lista = document.createElement("ol");
    lista.style.cssText = "margin:8px 0 0 20px;padding:0";
    function item(html) { var li = document.createElement("li"); li.style.marginBottom = "8px"; li.innerHTML = html; lista.appendChild(li); return li; }
    if (cc.entrada) {
      var li = item("Copie os bytes embaralhados da amostra:");
      var txt = document.createElement("textarea");
      txt.readOnly = true; txt.rows = 2; txt.value = cc.entrada;
      txt.style.cssText = "display:block;width:100%;margin:6px 0;background:#08060a;color:#ffd9ec;border:1px solid #ff2f9a;font:12px monospace;padding:6px;box-sizing:border-box";
      var bt = document.createElement("button");
      bt.textContent = "Copiar";
      bt.style.cssText = "background:#ff2f9a;color:#000;border:0;border-radius:4px;padding:3px 12px;cursor:pointer";
      bt.onclick = function () {
        txt.select();
        (navigator.clipboard ? navigator.clipboard.writeText(cc.entrada) : Promise.reject()).then(function () {
          bt.textContent = "Copiado";
        }).catch(function () { bt.textContent = "Use Ctrl+C"; });
      };
      li.appendChild(txt); li.appendChild(bt);
    } else {
      item(cc.origem);
    }
    item(site + " (outra aba). Cole no quadro Input, à direita.");
    cc.receita.forEach(item);
    item("O resultado aparece no quadro Output, embaixo à direita. Leve a resposta pro campo aqui do jogo.");
    caixa.innerHTML = "<b>O CyberChef desfaz o embaralhamento pra você.</b>";
    caixa.appendChild(lista);
    area.innerHTML = ""; area.appendChild(caixa);
  }

  // Ferramentas que no VM abrem janela: aqui ficam na propria tela.
  function abrir(casoId, tool, area) {
    var c = caso(casoId);
    if (tool === "terminal" || tool === "yara") { abrirTerminal(c, area); return true; }
    if (tool === "xor") { abrirCyberChef(c, area); return true; }
    return false;
  }

  return { api: api, abrir: abrir };
})();
