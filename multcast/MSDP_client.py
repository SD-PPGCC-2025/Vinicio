# rp2.py

import socket
import struct
import threading
import time
import random

MCAST_PORT = 5007

local_sources = {
    '224.2.2.2': True
}

joined_groups = set()

def udp_sender(mcast_grp):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    while True:
        humidity = round(random.uniform(40, 60), 2)
        msg = f"RP2-Sensor@{mcast_grp} HUM:{humidity}"
        sock.sendto(msg.encode(), (mcast_grp, MCAST_PORT))
        print(f"[RP2 UDP Sender] Sent: {msg}")
        time.sleep(10)

def udp_receiver(mcast_grp):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print(f"[RP2 UDP Receiver] Listening on {mcast_grp}:{MCAST_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"[RP2 UDP Receiver] Received from {addr}: {data.decode()}")

def msdp_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 10000))
    print("[RP2 MSDP] Connected to RP1 MSDP server")

    # Envia suas fontes para RP1
    for group in local_sources.keys():
        msg = f"SA {group}"
        client.sendall(msg.encode())

    while True:
        data = client.recv(1024)
        if not data:
            break
        msg = data.decode()
        print(f"[RP2 MSDP] Received: {msg}")
        if msg.startswith("SA"):
            _, group = msg.split()
            if group not in joined_groups:
                print(f"[RP2 MSDP] Joining multicast group {group} devido anúncio MSDP")
                joined_groups.add(group)
                threading.Thread(target=udp_receiver, args=(group,), daemon=True).start()

    client.close()

if __name__ == "__main__":
    for group in local_sources.keys():
        threading.Thread(target=udp_sender, args=(group,), daemon=True).start()

    for group in local_sources.keys():
        threading.Thread(target=udp_receiver, args=(group,), daemon=True).start()

    msdp_client()
