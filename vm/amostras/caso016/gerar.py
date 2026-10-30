#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Caso 016 (intermediario): DNS TUNNELING. INOFENSIVO (so um arquivo .pcap).
# Diferente do Caso 016 (beacon HTTP + cookie base64 sobre TCP): aqui a
# exfiltracao e so por DNS. O segredo e fatiado, cada pedaco vira HEX e e
# mandado como um subdominio numa consulta A. O aluno lista as consultas no
# tshark, junta os rotulos, decodifica o hex e recupera o segredo.
import struct
import socket

VICTIM = "192.168.56.101"
DNS_SRV = "192.168.56.1"
DOMAIN = "data.exfil-dns.net"
SEGREDO = "senha=panthera_2024"

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


def udp(sp, dp, payload):
    return struct.pack("!HHHH", sp, dp, 8 + len(payload), 0) + payload


def eth(src, dst, ethertype, payload):
    return dst + src + struct.pack("!H", ethertype) + payload


def dns_query(name, ident):
    hdr = struct.pack("!HHHHHH", ident, 0x0100, 1, 0, 0, 0)
    q = b"".join(struct.pack("B", len(p)) + p.encode() for p in name.split(".")) + b"\x00"
    q += struct.pack("!HH", 1, 1)   # tipo A, classe IN
    return hdr + q


# Fatiamos o HEX do segredo em pedacos de 8 digitos (4 bytes) por consulta.
hexseg = SEGREDO.encode().hex()
chunks = [hexseg[i:i + 8] for i in range(0, len(hexseg), 8)]
nomes = ["%s.%s" % (c, DOMAIN) for c in chunks]

pacotes = [
    eth(MAC_A, MAC_B, 0x0800,
        ipv4(VICTIM, DNS_SRV, 17, udp(51000 + i, 53, dns_query(n, 0x3000 + i)), i + 1))
    for i, n in enumerate(nomes)
]


def pcap_bytes():
    out = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)   # Ethernet
    for i, p in enumerate(pacotes):
        out += struct.pack("<IIII", 1700000000 + i * 5, 0, len(p), len(p)) + p
    return out


with open("tunnel.pcap", "wb") as f:
    f.write(pcap_bytes())

print("gerado tunnel.pcap (%d consultas DNS)." % len(pacotes))
print("segredo=%r  hex=%s  rotulos=%s" % (SEGREDO, hexseg, [c for c in chunks]))
