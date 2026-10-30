# Packer template do Quarentena.
# Monta a VM (Ubuntu 22.04 + desktop XFCE + ferramentas reais + curso) e exporta
# um .ova que o VMware Player/Workstation ABRE (File > Open), alem do VirtualBox.
#   packer init quarentena.pkr.hcl
#   packer build quarentena.pkr.hcl
#
# Usa o builder VirtualBox porque o Packer so builda com VMware WORKSTATION (nao
# com o Player). O .ova gerado e portavel e importa no VMware Player.
packer {
  required_plugins {
    virtualbox = {
      source  = "github.com/hashicorp/virtualbox"
      version = ">= 1.0.5"
    }
  }
}

source "virtualbox-iso" "quarentena" {
  iso_url      = "https://releases.ubuntu.com/22.04/ubuntu-22.04.5-live-server-amd64.iso"
  iso_checksum = "file:https://releases.ubuntu.com/22.04/SHA256SUMS"

  guest_os_type        = "Ubuntu_64"
  disk_size            = 30000
  guest_additions_mode = "disable"
  headless             = true
  output_directory     = "D:/quarentena-build/output/quarentena"
  format               = "ova"
  vm_name              = "Quarentena"

  vboxmanage = [
    ["modifyvm", "{{.Name}}", "--memory", "4096"],
    ["modifyvm", "{{.Name}}", "--cpus", "2"],
    ["modifyvm", "{{.Name}}", "--vram", "64"],
    # disco antes do DVD: no 1o boot o disco vazio cai pro DVD (instalador);
    # depois de instalar, o disco vira bootavel e a VM NAO reabre o instalador.
    ["modifyvm", "{{.Name}}", "--boot1", "disk", "--boot2", "dvd", "--boot3", "none", "--boot4", "none"],
  ]

  http_directory = "http"
  boot_wait      = "10s"
  boot_command = [
    "<wait>c<wait5>",
    "linux /casper/vmlinuz autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/<wait>",
    "<enter><wait5>",
    "initrd /casper/initrd<wait>",
    "<enter><wait5>",
    "boot<wait>",
    "<enter>"
  ]

  ssh_username = "analista"
  ssh_password = "analista"
  ssh_timeout  = "30m"

  shutdown_command = "sudo shutdown -P now"
}

build {
  name    = "quarentena"
  sources = ["source.virtualbox-iso.quarentena"]

  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '[provision] aguardando cloud-init/apt...'",
      "cloud-init status --wait 2>/dev/null || true",
      "sudo apt-get update -y",
      "sudo -E apt-get install -y git xfce4 xfce4-terminal lightdm firefox",
      "sudo mkdir -p /etc/lightdm/lightdm.conf.d",
      "printf '[Seat:*]\\nautologin-user=analista\\nuser-session=xfce\\n' | sudo tee /etc/lightdm/lightdm.conf.d/50-quarentena.conf >/dev/null",
      "sudo systemctl set-default graphical.target",
      "git clone --depth 1 https://github.com/marianabsctba/Quarentena.git $HOME/quarentena-src",
      "cp -r $HOME/quarentena-src/vm $HOME/quarentena",
      "bash $HOME/quarentena/provision.sh || echo '[provision] terminou com avisos'",
      "mkdir -p $HOME/Desktop",
      "printf '[Desktop Entry]\\nType=Application\\nName=Quarentena\\nComment=Primeiro dia de estagio em engenharia reversa\\nExec=bash %s/quarentena/guia/iniciar.sh\\nTerminal=true\\nIcon=utilities-terminal\\n' \"$HOME\" > $HOME/Desktop/Quarentena.desktop",
      "chmod +x $HOME/Desktop/Quarentena.desktop",
      "echo '[provision] CONCLUIDO.'"
    ]
  }
}
