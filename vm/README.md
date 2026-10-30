# Quarentena na VM (ferramentas reais)

Esta pasta é o coração do jogo "de verdade": um ambiente 3D (o setor de
Engenharia Reversa da Panthera Quarentena) que roda **dentro de uma VM Linux** e, por
baixo, **abre as ferramentas reais** (Ghidra, radare2, Wireshark, strings,
readelf...) sobre amostras didáticas e inofensivas. É o primeiro dia de estágio.

## Como funciona

```
[ Navegador na VM ]  <->  [ servidor.py (local, 127.0.0.1) ]  ->  ferramentas REAIS
   ambiente 3D (web)          serve o 3D e a API                 (Ghidra, strings,
   guia/missoes               roda/abre as ferramentas            readelf, strace...)
                              confere as respostas
```

- `guia/web/` : o front-end 3D (offline: three.js e o logo são locais).
- `guia/servidor.py` : o servidor local. Serve o 3D e expõe a API que **roda as
  ferramentas de linha de comando reais** (saída aparece no 3D) e **abre as GUI
  reais** (Ghidra etc.), além de conferir as respostas (o hash é conferido de
  verdade pelo servidor).
- `guia/curso.py` : o conteúdo do curso (o Caso 001, do zero ao laudo), técnico
  e com o veterano soltando piada.
- `amostras/` : as amostras didáticas, compiladas de **fonte C benigna**. Nunca
  malware de verdade.

## Rodar (desenvolvimento, em qualquer Linux com as ferramentas)

```bash
cd vm/guia
python3 servidor.py
# abra http://127.0.0.1:8777 no navegador
```

O servidor compila a amostra sozinho na primeira vez (precisa de `gcc` e
`python3`). As ferramentas de texto (strings, readelf, objdump, xxd, strace)
aparecem na própria tela; Ghidra e Wireshark abrem como programas.

## Montar a VM

### Opção A: Vagrant (um comando)

Com [Vagrant](https://www.vagrantup.com/) + VirtualBox instalados no host:

```bash
cd vm
vagrant up            # sobe a VM Ubuntu, instala o desktop e roda o provision.sh
vagrant reload        # reinicia pra cair no desktop gráfico
```

O `Vagrantfile` usa a box `bento/ubuntu-22.04`, instala o desktop XFCE, copia o
jogo pra `~/quarentena` e roda o `provision.sh` sozinho (4 GB de RAM, 2 CPUs).
No desktop, clique no atalho **Quarentena** (ou rode
`bash ~/quarentena/guia/iniciar.sh`). Para VMware Desktop/Fusion: instale o
plugin `vagrant-vmware-desktop` e rode `vagrant up --provider vmware_desktop`.

### Opção B: VM manual

Crie uma VM **Ubuntu desktop** limpa no VMware ou VirtualBox (com interface
gráfica, porque Ghidra, Wireshark e o navegador são GUIs). Com internet **só
nesta etapa**:

```bash
bash vm/provision.sh
```

O `provision.sh` (idempotente, e reporta um resumo de avisos no fim):

1. instala via apt as ferramentas reais: `gcc`/`binutils` (objdump, readelf,
   nm), `xxd`, `file`, `strace`, `ltrace`, `radare2`, `yara`, **`upx`**
   (upx-ucl), `wireshark`/`tshark`, `firefox`, JRE e um terminal;
2. baixa e instala o **Ghidra** (pega a release mais recente pela API do
   GitHub e cria o `ghidraRun` no PATH);
3. baixa o **CyberChef offline** para `guia/web/cyberchef.html` (a VM fica
   isolada, então nada de versão online);
4. compila/gera **todas as 30 amostras** (o Caso 022/UPX só empacota de
   verdade aqui, porque depende do `upx`);
5. confere se cada ferramenta está no PATH.

Depois:

```bash
bash vm/guia/iniciar.sh
```

### Confira que ficou tudo funcionando (na VM)

```bash
command -v ghidraRun upx yara radare2 tshark objdump   # todas devem responder
ls vm/guia/web/cyberchef.html                           # CyberChef offline presente
ghidraRun &                                             # abre a GUI do Ghidra
```

No jogo, teste um caso de cada ferramenta GUI: um que peça **Ghidra** (ex: 019),
o de **UPX** (022, precisa do `upx`) e um de **CyberChef** (abre o HTML local).
As ferramentas de texto (strings, readelf, objdump, xxd, strace, tshark) já
aparecem na própria tela e são testadas no `provision.sh`.

Recomendado para a aula: tirar um **snapshot** e **desligar a rede** da VM. O
servidor só escuta em `127.0.0.1`, e as amostras são inofensivas, mas isolar é
o hábito certo (e o jogo ensina isso no primeiro dia).

## Segurança

As amostras não conectam em lugar nenhum, não persistem de verdade e não atacam
nada. Elas apenas carregam traços reais (string XOR, anti-debug com ptrace,
símbolos legíveis) para o estudante treinar com as ferramentas de verdade.
