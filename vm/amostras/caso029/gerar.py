#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 029 (mestre): REVERSAO DE PROTOCOLO de C2. INOFENSIVO (so um .pcap).
# O trafego usa um protocolo binario proprio (nao HTTP). Cada mensagem segue o
# formato: magic (BE EF) + opcode (1 byte) + tamanho (1 byte) + payload. O aluno
# olha os bytes no tshark, deduz o formato e extrai o conteudo das mensagens.
import struct
import socket

VICTIM = "192.168.56.101"
C2_IP = "203.0.113.77"          # faixa de documentacao, inofensiva
MAGIC = b"\xbe\xef"
MAC_A = b"\x02\x00\x00\x00\x00\x01"
MAC_B = b"\x02\x00\x00\x00\x00\x02"


def msg(opcode, payload):
    return MAGIC + bytes([opcode, len(payload)]) + payload


# opcode 0x01 = REGISTRO (envia o hostname); 0x02 = PING; 0x03 = TAREFA
mensagens = [
    msg(0x01, b"FIN-PC"),
    msg(0x02, b"alive"),
    msg(0x03, b"coletar-docs"),
]


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


pacotes = []
for i, m in enumerate(mensagens):
    pacotes.append(eth(MAC_A, MAC_B, 0x0800,
                       ipv4(VICTIM, C2_IP, 6, tcp(49300, 8443, 1000 + i, 1, 0x18, m), i + 1)))


def pcap_bytes():
    out = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    for i, p in enumerate(pacotes):
        out += struct.pack("<IIII", 1700000000 + i, 0, len(p), len(p)) + p
    return out


with open("proto.pcap", "wb") as f:
    f.write(pcap_bytes())

print("gerado proto.pcap (%d mensagens). magic=be ef, formato: magic+opcode+len+payload" % len(pacotes))
for m in mensagens:
    print("  bytes:", m.hex(), "payload:", m[4:].decode())
