# rp1.py

import socket
import struct
import threading
import time
import random
lock = threading.Lock()
clients = []      

MCAST_PORT = 5007

lock = threading.Lock()         
clients = []                    

joined_groups = set()

local_sources = {
    '224.1.1.1': True
}

def udp_sender(mcast_grp):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    while True:
        temp = round(random.uniform(20, 30), 2)
        msg = f"RP1-Sensor@{mcast_grp} TEMP:{temp}"
        sock.sendto(msg.encode(), (mcast_grp, MCAST_PORT))
        print(f"[RP1 UDP Sender] Sent: {msg}")
        time.sleep(10)

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

def client_handler(conn, addr):
    global clients, joined_groups
    print(f"[RP1 MSDP] Client connected: {addr}")

    # Enviar anúncios armazenados para cliente novo
    with lock:
        for group in local_sources.keys():
            conn.sendall(f"SA {group}\n".encode())
        for group in joined_groups:
            conn.sendall(f"SA {group}\n".encode())

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            print(f"[RP1 MSDP] Received from {addr}: {msg}")

            if msg.startswith("SA"):
                _, group = msg.split()
                with lock:
                    if group not in joined_groups and group not in local_sources:
                        print(f"[RP1 MSDP] Joining multicast group {group} due to announcement from {addr}")
                        joined_groups.add(group)
                        threading.Thread(target=udp_receiver, args=(group,), daemon=True).start()

                    # Repassar anúncio para outros clientes
                    for c in clients:
                        if c != conn:
                            try:
                                c.sendall(f"SA {group}\n".encode())
                            except Exception as e:
                                print(f"[RP1 MSDP] Error sending to client: {e}")
    except Exception as e:
        print(f"[RP1 MSDP] Connection error with {addr}: {e}")
    finally:
        with lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[RP1 MSDP] Client disconnected: {addr}")

def msdp_server():
    global clients
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(('localhost', 10000))
    srv.listen(5)
    print("[RP1 MSDP] Listening for MSDP connections on TCP 10000")

    while True:
        conn, addr = srv.accept()
        with lock:
            clients.append(conn)
        threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()



if __name__ == "__main__":
    try:
        # Inicia UDP sender para fontes locais
        for group in local_sources.keys():
            threading.Thread(target=udp_sender, args=(group,), daemon=True).start()

        # Inicia UDP receptor para grupos locais
        for group in local_sources.keys():
            threading.Thread(target=udp_receiver, args=(group,), daemon=True).start()

        # Inicia servidor MSDP
        msdp_server()
    except KeyboardInterrupt:
        print("Receiver stopped.")