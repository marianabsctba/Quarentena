#!/usr/bin/env bash
# Monta o Linux que roda no navegador: Alpine x86 (32 bits, unico modo do v86)
# com as ferramentas reais e as amostras compiladas de fonte. Precisa de root
# para o chroot. Saidas em pages/saida/site/fs: fs.json, flat/ e sha256.txt.
set -euo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../.." && pwd)"
SAIDA="$RAIZ/pages/saida/site/fs"
TRAB="${TRAB:-/tmp/quarentena-imagem}"
ALPINE="3.21.9"
ROOTFS="$TRAB/rootfs"
AUX="$TRAB/aux"   # chroot so com o que o empacotador do v86 precisa

desmontar() {
  for m in "$ROOTFS"/proc "$ROOTFS"/sys "$ROOTFS"/dev "$AUX"/dev; do
    umount -l "$m" 2>/dev/null || true
  done
}
trap desmontar EXIT

desmontar
rm -rf "$TRAB"
mkdir -p "$ROOTFS" "$AUX"

echo "[1/6] Alpine $ALPINE x86"
curl -fsSL -o "$TRAB/mini.tar.gz" \
  "https://dl-cdn.alpinelinux.org/alpine/v${ALPINE%.*}/releases/x86/alpine-minirootfs-$ALPINE-x86.tar.gz"
tar xzf "$TRAB/mini.tar.gz" -C "$ROOTFS"
tar xzf "$TRAB/mini.tar.gz" -C "$AUX"
cp /etc/resolv.conf "$AUX/etc/resolv.conf"
mount --rbind /dev "$AUX/dev"
chroot "$AUX" /sbin/apk add --no-cache --quiet python3 py3-zstandard
cp /etc/resolv.conf "$ROOTFS/etc/resolv.conf"
mount -t proc proc "$ROOTFS/proc"
mount -t sysfs sys "$ROOTFS/sys"
mount --rbind /dev "$ROOTFS/dev"

echo "[2/6] Ferramentas reais"
chroot "$ROOTFS" /sbin/apk add --no-cache --quiet \
  openrc alpine-base agetty alpine-conf linux-virt linux-firmware-none \
  bash binutils file strace xxd python3 yara tshark upx \
  gcc musl-dev

echo "[3/6] Amostras (compiladas de fonte, inofensivas)"
mkdir -p "$ROOTFS/casos"
cp -r "$RAIZ"/vm/amostras/caso* "$ROOTFS/casos/"
for d in "$ROOTFS"/casos/caso*; do
  c="$(basename "$d")"
  chroot "$ROOTFS" /bin/bash -c "bash /casos/$c/build.sh" >/dev/null
done
# O aluno recebe so a amostra: a fonte entregaria a resposta.
find "$ROOTFS/casos" -type f \( -name gerar.py -o -name fonte.c -o -name build.sh \
  -o -name README.md -o -name '*.o' -o -name '.tmp*' \) -delete
(cd "$ROOTFS/casos" && find . -type f | sort | xargs sha256sum) > "$TRAB/sha256.txt"

echo "[4/6] Sistema: autologin, agente e initramfs"
chroot "$ROOTFS" /sbin/apk del --no-cache --quiet gcc musl-dev
install -m 755 "$AQUI/agente.sh" "$ROOTFS/usr/local/bin/agente"
install -m 755 "$AQUI/entropia.py" "$ROOTFS/usr/local/bin/entropia"
sed -i 's/^tty[0-9].*//' "$ROOTFS/etc/inittab"
cat >> "$ROOTFS/etc/inittab" <<'EOF'
ttyS0::respawn:/sbin/agetty --autologin root -s ttyS0 115200 vt100
ttyS1::respawn:/usr/local/bin/agente
EOF
cat > "$ROOTFS/etc/profile.d/quarentena.sh" <<'EOF'
export PS1='analista@panthera:\w\$ '
EOF
cat > "$ROOTFS/etc/motd" <<'EOF'
Panthera Quarentena, setor de Engenharia Reversa. Linux real, dentro da sua aba.
Sem rede. Recarregar a pagina volta tudo ao zero. As amostras estao em /casos.
EOF
: > "$ROOTFS/etc/resolv.conf"
chroot "$ROOTFS" /bin/sh -c '
  echo "root:" | chpasswd
  setup-hostname panthera
  for s in devfs dmesg mdev; do rc-update add $s sysinit; done
  for s in modules sysctl hostname bootmisc; do rc-update add $s boot; done
  rc-update add killprocs shutdown
  mkinitfs -F "base virtio 9p" "$(cat /usr/share/kernel/virt/kernel.release)"
' >/dev/null
rm -rf "$ROOTFS"/var/cache/apk/* "$ROOTFS"/lib/modules/*/kernel/drivers/{gpu,net/wireless,media,infiniband,scsi} \
  "$ROOTFS"/usr/share/man "$ROOTFS"/usr/share/doc
desmontar

echo "[5/6] Empacotando"
# Sem o "./" na frente: o fs2json monta a arvore pelos nomes do tar.
(cd "$ROOTFS" && tar --numeric-owner -cf "$AUX/rootfs.tar" $(ls -A))
cp "$AQUI/v86/fs2json.py" "$AQUI/v86/copy-to-sha256.py" "$AUX/"

echo "[6/6] Formato do v86"
mkdir -p "$AUX/saida/flat"
chroot "$AUX" /bin/sh -c '
  python3 /fs2json.py --zstd --out /saida/fs.json /rootfs.tar
  python3 /copy-to-sha256.py --zstd /rootfs.tar /saida/flat
'
rm -rf "$SAIDA"
mkdir -p "$(dirname "$SAIDA")"
cp -r "$AUX/saida" "$SAIDA"
cp "$TRAB/sha256.txt" "$SAIDA/sha256.txt"
du -sh "$SAIDA"
find "$SAIDA/flat" -type f | wc -l
echo "ok: $SAIDA"
