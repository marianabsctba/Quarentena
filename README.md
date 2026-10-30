# Panthera Quarentena

> Primeiro dia de estágio no setor de Engenharia Reversa. O café é ruim, a pilha de casos é alta e o veterano não para de fazer piada.

**[Jogar no navegador](https://marianabsctba.github.io/Panthera_Quarentena/)**

Panthera Quarentena é um jogo que ensina **engenharia reversa de malware** com
**ferramentas reais**, sem instalar nada. Um Linux de verdade sobe dentro da aba
do navegador, sem rede. Você entra num escritório em 3D, um veterano te guia caso
a caso e o trabalho acontece de verdade: a amostra chega, você analisa e descobre
o que ela faz.

São **30 casos**, do iniciante ao mestre, cada um com uma técnica diferente. Veja
o [currículo](vm/CURRICULO.md).

As amostras são **didáticas e inofensivas**: compiladas de fonte benigna no build,
elas só carregam traços reais (string ofuscada com XOR, anti-debug com ptrace,
overlay, API hashing) para o estudante treinar. Nunca malware de verdade.

## Ferramentas

`file`, `sha256sum`, `xxd`, `strings`, `readelf`, `objdump`, `strace`, `tshark`,
`yara`, `upx`, `python3` e um terminal de verdade. O CyberChef abre em outra aba.

## Como funciona

```
[ Aba do navegador ]
   ambiente 3D, guia e terminal
        |
   Linux real (Alpine de 32 bits no emulador v86)
        |
   ferramentas reais sobre as amostras
```

Tudo roda no seu navegador: não há servidor, e o site só entrega os arquivos. O
primeiro acesso baixa cerca de 25 MB e depois fica em cache. Recarregar a página
volta o laboratório ao zero. As respostas são conferidas na própria página, então
quem quiser consegue ver o gabarito no código: é um jogo de estudo.

## Estrutura

```
pages/          versão do navegador: imagem do Linux, site e teste dos casos
vm/guia/        curso (casos, passos, o veterano) e ambiente 3D
vm/amostras/    amostras didáticas (fonte benigna + build)
vm/             versão alternativa, instalada numa VM Linux
arte/           identidade (o logo da pantera)
```

Para gerar o site localmente, veja [pages/LEIAME.md](pages/LEIAME.md). Para
instalar numa VM própria, veja [vm/README.md](vm/README.md).

## Licença

MIT. Veja [LICENSE](LICENSE).
