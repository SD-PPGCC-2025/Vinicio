# rp1.py

import socket
import struct
import threading
import time
import random

MCAST_PORT = 5007

# Multicast groups locais do RP1
local_sources = {
    '224.1.1.1': True  # RP1 tem uma fonte nesse grupo
}

joined_groups = set()

def udp_sender(mcast_grp):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    while True:
        temp = round(random.uniform(20, 30), 2)
        msg = f"RP1-Sensor@{mcast_grp} TEMP:{temp}"
        sock.sendto(msg.encode(), (mcast_grp, MCAST_PORT))
        print(f"[RP1 UDP Sender] Sent: {msg}")
        time.sleep(3)

def udp_receiver(mcast_grp):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print(f"[RP1 UDP Receiver] Listening on {mcast_grp}:{MCAST_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"[RP1 UDP Receiver] Received from {addr}: {data.decode()}")

def msdp_server():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(('localhost', 10000))
    srv.listen(1)
    print("[RP1 MSDP] Listening for MSDP connections on TCP 10000")
    conn, addr = srv.accept()
    print(f"[RP1 MSDP] Connected by {addr}")

    # Envia inicialmente suas fontes
    for group in local_sources.keys():
        msg = f"SA {group}"
        conn.sendall(msg.encode())

    while True:
        data = conn.recv(1024)
        if not data:
            break
        msg = data.decode()
        print(f"[RP1 MSDP] Received: {msg}")
        if msg.startswith("SA"):
            # Recebe anúncio de fonte do RP2
            _, group = msg.split()
            if group not in joined_groups:
                print(f"[RP1 MSDP] Joining multicast group {group} devido anúncio MSDP")
                joined_groups.add(group)
                # Inicia receptor UDP para essa fonte
                threading.Thread(target=udp_receiver, args=(group,), daemon=True).start()

    conn.close()

if __name__ == "__main__":
    # Inicia UDP sender para fontes locais
    for group in local_sources.keys():
        threading.Thread(target=udp_sender, args=(group,), daemon=True).start()

    # Inicia UDP receptor para grupos locais
    for group in local_sources.keys():
        threading.Thread(target=udp_receiver, args=(group,), daemon=True).start()

    # Inicia servidor MSDP
    msdp_server()
