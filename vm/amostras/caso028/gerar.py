#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 028 (mestre): C2 CIFRADO num pcap. INOFENSIVO (so um arquivo .pcap).
# O trafego pro C2 nao vai em texto puro: o payload TCP esta XORado com uma
# chave de 1 byte (0x5A). O aluno extrai o payload no tshark e decifra pra ler
# o comando. Nenhum pacote e enviado.
import struct
import socket

VICTIM = "192.168.56.101"
C2_IP = "203.0.113.55"          # faixa de documentacao (TEST-NET-3), inofensiva
KEY = 0x5A
COMANDO = "CMD:coletar;alvo=FIN-PC;destino=203.0.113.55"
MAC_A = b"\x02\x00\x00\x00\x00\x01"
MAC_B = b"\x02\x00\x00\x00\x00\x02"


def checksum(data):
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return (~s) & 0xffff


def ipv4(src, dst, proto, payload, ident):
    total = 20 + len(payload)
    hdr = struct.pack("!BBHHHBBH4s4s", 0x45, 0, total, ident, 0, 64, proto, 0,
                      socket.inet_aton(src), socket.inet_aton(dst))
    chk = checksum(hdr)
    hdr = struct.pack("!BBHHHBBH4s4s", 0x45, 0, total, ident, 0, 64, proto, chk,
                      socket.inet_aton(src), socket.inet_aton(dst))
    return hdr + payload


def tcp(sp, dp, seq, ack, flags, payload=b""):
    return struct.pack("!HHIIBBHHH", sp, dp, seq, ack, (5 << 4), flags, 65535, 0, 0) + payload


def eth(src, dst, ethertype, payload):
    return dst + src + struct.pack("!H", ethertype) + payload


cifrado = bytes(b ^ KEY for b in COMANDO.encode())
pacotes = [
    eth(MAC_A, MAC_B, 0x0800, ipv4(VICTIM, C2_IP, 6, tcp(49210, 50100, 1000, 1, 0x18, cifrado), 1)),
]


def pcap_bytes():
    out = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    for i, p in enumerate(pacotes):
        out += struct.pack("<IIII", 1700000000 + i, 0, len(p), len(p)) + p
    return out


with open("c2.pcap", "wb") as f:
    f.write(pcap_bytes())

print("gerado c2.pcap. chave XOR=0x%02x" % KEY)
print("payload_cifrado_hex=" + cifrado.hex())
print("comando_claro=" + COMANDO)
