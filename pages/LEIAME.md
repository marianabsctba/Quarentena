# Quarentena no GitHub Pages

Versão que roda inteira no navegador: um Linux real (Alpine de 32 bits) sobe na
aba com o [v86](https://github.com/copy/v86), sem servidor e sem rede. As
ferramentas são as de verdade (`file`, `xxd`, `strings`, `readelf`, `objdump`,
`strace`, `tshark`, `yara`, `upx`, `python3`), e as amostras são compiladas de
fonte no build, inofensivas como na VM.

## Gerar localmente

Precisa de Linux com root (o WSL serve) e Node 24.

```bash
sudo bash pages/imagem/construir.sh
cd pages
npm ci
python3 gerar_site.py
node gerar_estado.mjs
node testar.mjs
python3 -m http.server --directory saida/site
```

`testar.mjs` joga os 30 casos sem navegador e lista as respostas que não
aparecem na saída direta da ferramenta. Algumas são esperadas, como IDs do MITRE
e textos que o aluno precisa decodificar.

O deploy roda em `.github/workflows/pages.yml` a cada push na `main`.
