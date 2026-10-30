// Liga o Linux uma vez e salva a memoria ja bootada. O site restaura esse estado
// em vez de bootar do zero. Uso (depois de gerar o site): node gerar_estado.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(AQUI, "saida", "site");
const require = createRequire(import.meta.url);
const { V86 } = require("v86");

const t0 = Date.now();
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

let buf = "", shell = "";
let responder = null;
emu.add_listener("serial1-output-byte", (b) => {
  if (b !== 10) { buf += String.fromCharCode(b); return; }
  const fim = /FIM 0/.test(buf); buf = "";
  if (fim && responder) responder();
});
emu.add_listener("serial0-output-byte", (b) => { shell += String.fromCharCode(b); });

await new Promise((ok) => {
  const ping = setInterval(() => emu.serial_send_bytes(1, Buffer.from("0 - - -\n")), 1500);
  responder = () => { clearInterval(ping); responder = null; ok(); };
});
console.log(`boot do zero: ${((Date.now() - t0) / 1000).toFixed(1)}s`);

// Espera o shell do aluno e limpa o cache do kernel: memoria zerada comprime melhor.
while (!shell.includes("analista@panthera")) await new Promise((r) => setTimeout(r, 200));
shell = "";
emu.serial0_send("sync; echo 3 > /proc/sys/vm/drop_caches; clear; echo __PR\"\"ONTO__\n");
while (!shell.includes("__PRONTO__")) await new Promise((r) => setTimeout(r, 200));
await new Promise((r) => setTimeout(r, 1500));

const estado = new Uint8Array(await emu.save_state());
const comprimido = zlib.zstdCompressSync(estado, {
  params: { [zlib.constants.ZSTD_c_compressionLevel]: 19 },
});
const versao = fs.readFileSync(path.join(AQUI, "saida", "versao.txt"), "utf8").trim();
const destino = path.join(SITE, `estado-${versao}.bin.zst`);
fs.writeFileSync(destino, comprimido);
console.log(`estado: ${(estado.length / 1e6).toFixed(0)} MB, comprimido ${(comprimido.length / 1e6).toFixed(1)} MB`);
emu.destroy();
process.exit(0);
