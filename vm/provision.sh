#!/usr/bin/env bash
# Provisiona uma VM Ubuntu (desktop) com as ferramentas REAIS + o Quarentena.
# Rode DENTRO da VM. Precisa de internet SO nesta etapa; depois a VM pode (e
# deve) ficar isolada. Nao usa 'set -e' global: cada etapa reporta no resumo.
AQUI="$(cd "$(dirname "$0")" && pwd)"
WEB="$AQUI/guia/web"
export DEBIAN_FRONTEND=noninteractive   # apt sem prompt (ex: debconf do wireshark)
AVISOS=()
aviso(){ AVISOS+=("$1"); echo "    [!] $1"; }

echo "[*] (1/5) Ferramentas de engenharia reversa (apt)..."
# yara/upx/tshark/radare2 vivem no 'universe'; garante que ele esta habilitado
sudo apt-get install -y software-properties-common >/dev/null 2>&1 || true
sudo add-apt-repository -y universe >/dev/null 2>&1 || true
sudo apt-get update -y
# o tshark/wireshark pergunta no debconf; preseed pra nao travar a instalacao
echo 'wireshark-common wireshark-common/install-setuid boolean false' | sudo debconf-set-selections
# Essenciais: um pacote faltante NAO pode derrubar o resto (apt-get e atomico),
# entao deixamos o radare2 (as vezes fora do repo) por ultimo e opcional.
sudo -E apt-get install -y \
  build-essential gcc binutils xxd file strace ltrace \
  yara upx-ucl python3 python3-pip tshark firefox default-jre unzip wget curl xterm \
  || aviso "apt-get falhou em algum pacote essencial; confira a saida acima."
# radare2 e opcional: Ghidra + objdump ja cobrem a desmontagem do curso.
sudo -E apt-get install -y radare2 >/dev/null 2>&1 || aviso "radare2 indisponivel no apt (opcional, sem problema)."

echo "[*] (2/5) Ghidra (decompilador da NSA)..."
if command -v ghidraRun >/dev/null 2>&1; then
  echo "    ja instalado."
else
  GURL=$(wget -qO- https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/latest \
         | grep -oE 'https://[^"]+_PUBLIC_[0-9]+\.zip' | head -1)
  if [ -n "$GURL" ]; then
    echo "    baixando: $GURL"
    if wget -q -O /tmp/ghidra.zip "$GURL"; then
      sudo unzip -q -o /tmp/ghidra.zip -d /opt \
        && sudo ln -sf /opt/ghidra_*/ghidraRun /usr/local/bin/ghidraRun \
        && echo "    ok: ghidraRun em /usr/local/bin" || aviso "falha ao descompactar/instalar o Ghidra."
      rm -f /tmp/ghidra.zip
    else
      aviso "download do Ghidra falhou (sem internet?)."
    fi
  else
    aviso "nao achei a URL da release do Ghidra (API do GitHub indisponivel?)."
  fi
fi

echo "[*] (3/5) CyberChef offline (a VM fica isolada; nada de versao online)..."
CCDIR="$WEB/cyberchef"
if [ -f "$CCDIR/index.html" ]; then
  echo "    ja presente."
else
  # A release e um .zip (~83 MB) com o app inteiro: o HTML principal + as pastas
  # assets/images/modules ao lado. Descobre a tag pelo redirect de
  # /releases/latest (sem a API, que tem rate limit), baixa o .zip, extrai TUDO
  # e renomeia o HTML principal pra index.html (caminho estavel).
  TAG=$(wget -S --spider https://github.com/gchq/CyberChef/releases/latest 2>&1 \
        | grep -i 'location:' | grep -oE 'v[0-9.]+' | tail -1)
  ZIP=$(wget -qO- "https://github.com/gchq/CyberChef/releases/expanded_assets/$TAG" \
        | grep -oE '/gchq/CyberChef/releases/download/[^"]+\.zip' | head -1)
  if [ -n "$ZIP" ] && wget -q -O /tmp/cyberchef.zip "https://github.com${ZIP}"; then
    rm -rf "$CCDIR" && mkdir -p "$CCDIR"
    unzip -o -q /tmp/cyberchef.zip -d "$CCDIR"
    rm -f /tmp/cyberchef.zip
    MAIN=$(find "$CCDIR" -maxdepth 1 -name 'CyberChef_*.html' | head -1)
    [ -n "$MAIN" ] && mv -f "$MAIN" "$CCDIR/index.html"
  fi
  if [ -f "$CCDIR/index.html" ]; then
    echo "    ok ($TAG): $CCDIR/index.html"
  else
    rm -rf "$CCDIR"
    aviso "nao baixei o CyberChef offline; o passo de CyberChef cairia pra versao online."
  fi
fi

echo "[*] (4/5) Compilando/gerando TODAS as amostras didaticas (inofensivas)..."
FALHAS=()
for b in "$AQUI"/amostras/caso*/build.sh; do
  d=$(dirname "$b")
  if bash "$b" >/dev/null 2>&1; then
    echo "    ok: $(basename "$d")"
  else
    FALHAS+=("$(basename "$d")")
    aviso "build falhou em $(basename "$d") (rode 'bash $b' pra ver o erro)."
  fi
done

echo "[*] (5/5) Conferindo ferramentas no PATH..."
for t in gcc objdump readelf nm strings xxd file strace tshark yara upx python3 ghidraRun; do
  command -v "$t" >/dev/null 2>&1 || aviso "ferramenta ausente no PATH: $t"
done

echo
echo "============================================================"
if [ ${#AVISOS[@]} -eq 0 ]; then
  echo "[OK] Provisionamento completo, sem avisos."
else
  echo "[!] Provisionamento terminou com ${#AVISOS[@]} aviso(s):"
  for a in "${AVISOS[@]}"; do echo "    - $a"; done
fi
echo "------------------------------------------------------------"
echo "Para iniciar o Quarentena:"
echo "    bash $AQUI/guia/iniciar.sh"
echo "Recomendado para a aula: tire um SNAPSHOT e DESLIGUE a rede da VM."
echo "============================================================"
