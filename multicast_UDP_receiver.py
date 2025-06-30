# multicast_receiver.py

import socket
import struct

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))  # Escuta em todas as interfaces

# Join multicast group
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"[RECEIVER] Listening on {MCAST_GRP}:{MCAST_PORT}")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode('utf-8')
        print(f"[RECEIVER] Received from {addr}: {msg}")
        # Aqui, você pode processar os dados, armazenar em um banco de dados, enviar para nuvem etc.
except KeyboardInterrupt:
    print("Receiver stopped.")
