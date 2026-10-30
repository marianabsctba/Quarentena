// Liga o mesmo Linux do site, sem navegador, e joga todos os casos: roda cada
// ferramenta pedida e diz se a resposta do passo aparece na saida real. Tambem
// roda os comandos que os passos de terminal pressupoem.
// Uso (depois de gerar o site): node testar.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(AQUI, "saida", "site");
const require = createRequire(import.meta.url);
const { V86 } = require("v86");

const curso = JSON.parse(fs.readFileSync(path.join(SITE, "curso.json"), "utf8"));
const t0 = Date.now();
const seg = () => ((Date.now() - t0) / 1000).toFixed(1);

const emu = new V86({
  wasm_path: path.join(AQUI, "node_modules/v86/build/v86.wasm"),
  memory_size: 256 * 1024 * 1024,
  vga_memory_size: 2 * 1024 * 1024,
  bios: { url: path.join(SITE, "vendor/seabios.bin") },
  vga_bios: { url: path.join(SITE, "vendor/vgabios.bin") },
  filesystem: { baseurl: path.join(SITE, "fs/flat/"), basefs: path.join(SITE, "fs/fs.json") },
  bzimage_initrd_from_filesystem: true,
  cmdline: "rw root=host9p rootfstype=9p rootflags=trans=virtio,cache=loose modules=virtio_pci tsc=reliable console=ttyS0",
  uart1: true,
  autostart: true,
  disable_keyboard: true,
  disable_mouse: true,
});

let buf = "", seq = 0, shell = "";
const esperando = {};
emu.add_listener("serial1-output-byte", (b) => {
  if (b !== 10) { buf += String.fromCharCode(b); return; }
  const m = /FIM (\d+)/.exec(buf); buf = "";
  if (m && esperando[m[1]]) { esperando[m[1]](); delete esperando[m[1]]; }
});
emu.add_listener("serial0-output-byte", (b) => { shell += String.fromCharCode(b); });

const enviar = (id, c, a, t) => emu.serial_send_bytes(1, Buffer.from(`${id} ${c} ${a} ${t}\n`));

await new Promise((ok) => {
  const id = String(++seq);
  esperando[id] = ok;
  const ping = setInterval(() => enviar(id, "-", "-", "-"), 1500);
  esperando[id] = () => { clearInterval(ping); ok(); };
});
console.log(`boot: agente respondeu em ${seg()}s`);

async function ferramenta(caso, arquivo, tool) {
  const ini = Date.now();
  await new Promise((ok) => { const id = String(++seq); esperando[id] = ok; enviar(id, caso, arquivo, tool); });
  const saida = Buffer.from(await emu.read_file("/var/lib/quarentena/saida")).toString("utf8");
  return { saida, ms: Date.now() - ini };
}

async function terminal(cmd, espera = 90000) {
  const fim = `__FIM${++seq}__`;
  shell = "";
  emu.serial0_send(`${cmd}; echo ${fim.slice(0, 3)}""${fim.slice(3)}\n`);
  const ini = Date.now();
  while (!shell.includes(fim) && Date.now() - ini < espera) await new Promise((r) => setTimeout(r, 200));
  return { saida: shell, ms: Date.now() - ini, ok: shell.includes(fim) };
}

const EXEC = new Set(["triagem", "entropia", "hex", "strings", "elf", "disasm", "strace", "cat", "tshark"]);
const tempos = {};
const achados = [];
let total = 0, conferidos = 0;
for (const c of curso.casos) {
  const cache = {};
  for (const p of c.passos) {
    total++;
    if (!EXEC.has(p.tool)) continue;
    if (!cache[p.tool]) {
      cache[p.tool] = await ferramenta(c.id, c.arquivo, p.tool);
      (tempos[p.tool] ||= []).push(cache[p.tool].ms);
    }
    const saida = cache[p.tool].saida.toLowerCase();
    const alvo = p.resposta_tipo === "sha256" ? c.sha256 : (p.contem || p.resposta).toLowerCase();
    conferidos++;
    if (!saida.includes(alvo)) {
      achados.push(`${c.id} ${p.id} [${p.tool}] alvo "${alvo}" fora da saida (${cache[p.tool].saida.length} bytes)`);
    }
  }
  // Os bytes que o CyberChef recebe pronto precisam ser os da amostra de verdade.
  for (const p of c.passos) {
    const hex = p.cyberchef && p.cyberchef.entrada;
    if (!hex) continue;
    const amostra = Buffer.from(await emu.read_file(`/casos/${c.id}/${c.arquivo}`));
    if (!amostra.includes(Buffer.from(hex, "hex"))) achados.push(`${c.id} ${p.id} bytes do CyberChef fora da amostra`);
  }
  console.log(`${c.id} ok (${seg()}s)`);
}
console.log(`\npassos: ${total}; com ferramenta automatica: ${conferidos}`);
console.log("tempo medio por ferramenta (ms):");
for (const [t, v] of Object.entries(tempos)) {
  console.log(`  ${t}: ${Math.round(v.reduce((a, b) => a + b) / v.length)}`);
}
console.log(`\nresposta nao encontrada na saida (${achados.length}):`);
achados.forEach((a) => console.log("  " + a));

console.log("\ncomandos de terminal:");
for (const cmd of [
  "cd /casos/caso026 && objdump -D -b binary -m i386:x86-64 shellcode.bin | head -20",
  "cd /casos/caso015 && tshark -r captura.pcap -Y http -T fields -e http.cookie | head -5",
  "cd /casos/caso022 && upx -d packed_update -o /tmp/u && file /tmp/u",
  "echo 'rule t { strings: $a = \"PANTHERA_CAPSTONE_v1\" condition: $a }' > /tmp/t.yar && yara /tmp/t.yar /casos/caso030/sample_x",
  "cd /casos/caso016 && tshark -r tunnel.pcap -T fields -e dns.qry.name | head -4",
  "cd /casos/caso029 && tshark -r proto.pcap -x | head -8",
  "cd /casos/caso021 && strings rc4_loader | grep -i panthera",
  "cd /casos/caso007 && ls -l nota_fiscal; tail -n 1 nota_fiscal | base64 -d; echo",
  "cd /casos/caso009 && python3 -c \"import dis,marshal; f=open('agente.pyc','rb'); f.read(16); dis.dis(marshal.load(f))\" | grep -E 'pyc-c2|example|net|beacon'",
  "cd /casos/caso011 && strace -e prctl ./svc_helper --arm",
  "cd /casos/caso013 && hostname FIN-SRV-01 && ./licenca_check --arm; hostname panthera",
  "cd /casos/caso024 && ./boot_tool; ls /tmp",
  "echo aGVsbG8= | base64 -d; echo; python3 -c 'print(1+1)'; ip link | grep -c eth",
]) {
  const r = await terminal(cmd);
  console.log(`--- ${cmd}\n[${r.ms} ms${r.ok ? "" : ", NAO TERMINOU"}]\n${r.saida.slice(-900)}`);
}
emu.destroy();
process.exit(0);
