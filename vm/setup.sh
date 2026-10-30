#!/usr/bin/env bash
# Ajusta uma VM Quarentena JA criada pra rodar liso no VMware.
# Rode DENTRO da VM, uma vez. Resolve de uma vez:
#   - copiar/colar e tela cheia (instala o VMware Tools)
#   - fim do "tudo preto" por inatividade (desliga apagar-tela e bloqueio)
#   - curso abrindo sozinho toda vez que a VM liga
#   - aplica a versao mais nova do front-end 3D (correcao do "voltar a sala")
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"   # .../vm

echo "[*] Atualizando o curso em ~/quarentena com a versao mais nova..."
rm -rf "$HOME/quarentena"
cp -r "$AQUI" "$HOME/quarentena"

echo "[*] Instalando VMware Tools (copiar/colar + ajuste de tela)..."
sudo apt-get update -y >/dev/null 2>&1 || true
if sudo DEBIAN_FRONTEND=noninteractive apt-get install -y open-vm-tools open-vm-tools-desktop >/dev/null 2>&1; then
  echo "    ok (copiar/colar funciona depois de reiniciar a VM)"
else
  echo "    [!] falhou (a VM esta sem internet?); copiar/colar pode continuar sem funcionar"
fi

echo "[*] Desligando apagar-tela e bloqueio (fim do 'tudo preto')..."
gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null || true
gsettings set org.gnome.desktop.screensaver lock-enabled false 2>/dev/null || true
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type nothing 2>/dev/null || true
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type nothing 2>/dev/null || true

echo "[*] Fazendo o curso abrir sozinho ao ligar a VM..."
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/quarentena.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Quarentena
Comment=Abre o curso 3D ao iniciar
Exec=bash $HOME/quarentena/guia/iniciar.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

echo
echo "============================================================"
echo "[OK] Ajuste completo."
echo "    - Reinicie a VM uma vez pra ativar o copiar/colar."
echo "    - Dai em diante o curso abre sozinho; nada de terminal."
echo "============================================================"
echo "[*] Iniciando o curso agora..."
bash "$HOME/quarentena/guia/iniciar.sh"
