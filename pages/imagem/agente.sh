#!/bin/sh
# Roda DENTRO do Linux do navegador, preso na segunda porta serial. Faz o papel
# do servidor.py: recebe "id caso arquivo ferramenta", roda a ferramenta real
# sobre a amostra e grava a saida em /var/lib/quarentena. Lista fixa, como no servidor.
MAX=24000
mkdir -p /var/lib/quarentena
stty -F /dev/ttyS1 115200 raw -echo 2>/dev/null

rodar() {
  case "$1" in
    triagem)  file "$2"; sha256sum "$2" ;;
    entropia) entropia "$2" ;;
    hex)      xxd "$2" ;;
    strings)  strings "$2" ;;
    elf)      readelf -hSsW "$2" ;;
    disasm)   objdump -d -M intel "$2" ;;
    strace)   strace -f -e trace=file,network "./$2" --arm ;;
    cat)      cat "$2" ;;
    tshark)   tshark -r "$2" ;;
    *)        echo "ferramenta desconhecida: $1" ;;
  esac
}

while read -r id caso arquivo ferramenta; do
  if cd "/casos/$caso" 2>/dev/null; then
    rodar "$ferramenta" "$arquivo" 2>&1 | head -c "$MAX" > /var/lib/quarentena/saida
  else
    echo "caso desconhecido: $caso" > /var/lib/quarentena/saida
  fi
  sync
  echo "FIM $id"
done < /dev/ttyS1 > /dev/ttyS1
