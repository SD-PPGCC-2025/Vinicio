# multicast_sender.py

import socket
import struct
import time
import random

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
ttl = struct.pack('b', 1)  # Time-To-Live baixo para LAN
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:
    while True:
        temp = round(random.uniform(20.0, 30.0), 2)
        humidity = round(random.uniform(40.0, 60.0), 2)
        msg = f"TEMP:{temp},HUM:{humidity}"
        sock.sendto(msg.encode('utf-8'), (MCAST_GRP, MCAST_PORT))
        print(f"[SENDER] Sent: {msg}")
        time.sleep(2)
except KeyboardInterrupt:
    print("Sender stopped.")
