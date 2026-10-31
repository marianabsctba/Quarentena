// Passa pela conferencia do site a resposta certa de todos os passos e uma
// lista de respostas erradas que nao podem colar. Nao precisa ligar o Linux.
// Uso (depois de gerar o site): node testar_respostas.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const curso = JSON.parse(fs.readFileSync(path.join(AQUI, "saida/site/curso.json"), "utf8"));
const js = fs.readFileSync(path.join(AQUI, "web/navegador.js"), "utf8");
const trecho = js.slice(js.indexOf("function normalizar"), js.indexOf("function api("));
const conferir = new Function(`${trecho}; return conferir;`)();

const erros = [];
const achar = (trecho) => {
  for (const c of curso.casos) for (const p of c.passos) if (p.pergunta.includes(trecho)) return [c, p];
  throw new Error(`pergunta nao encontrada: ${trecho}`);
};
const espera = (c, p, resposta, ok) => {
  if (conferir(c, p.id, resposta).ok !== ok) erros.push(`${c.id} ${p.id}: "${resposta}" deveria ${ok ? "valer" : "ser recusada"}`);
};

let passos = 0;
for (const c of curso.casos) {
  for (const p of c.passos) {
    passos++;
    espera(c, p, p.resposta_tipo === "sha256" ? c.sha256 : p.resposta, true);
    for (const alvo of [].concat(p.contem || [])) espera(c, p, alvo, true);
    espera(c, p, "resposta errada", false);
    espera(c, p, "", false);
    const sn = [].concat(p.contem || [])[0];
    if (sn === "sim" || sn === "nao") {
      espera(c, p, "sim/não", false);
      espera(c, p, sn === "sim" ? "SIM" : "NÃO", true);
      espera(c, p, sn === "sim" ? "não" : "sim", false);
      espera(c, p, "simples", false);
    }
  }
}

const cpus = achar("Quantas CPUs");
["12", "20", "0x12"].forEach((r) => espera(...cpus, r, false));
["2", "2 CPUs", " 2 "].forEach((r) => espera(...cpus, r, true));
const chave = achar("A chave do XOR tem quantos");
["14", "40"].forEach((r) => espera(...chave, r, false));
["4", "4 bytes"].forEach((r) => espera(...chave, r, true));
const key = achar("Qual a chave usada em decrypt_strings");
["12a", "2a00"].forEach((r) => espera(...key, r, false));
["2a", "0x2A", "2A"].forEach((r) => espera(...key, r, true));

console.log(`${passos} passos conferidos, ${erros.length} erros`);
erros.forEach((e) => console.log("  " + e));
process.exit(erros.length ? 1 : 0);
