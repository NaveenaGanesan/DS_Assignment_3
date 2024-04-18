# server.py

import socket
from ntp_packet import Packet
import struct
import time

UDP_IP = "127.0.0.1"
# UDP_IP = "128.110.216.170"
# UDP_IP = "10.0.0.49"
UDP_PORT = 5096

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

print("Server started on ",UDP_IP)
sock.settimeout(244)

while True:
    # positive acknowledgment
    try:
        data, addr = sock.recvfrom(64) # buffer size is 1024 bytes
    except socket.timeout:
        print("Experienced timeout. Retrying")
        sock.sendto(data,addr)
        continue
        

    rec = time.time()
    ntp = Packet()
    ntp.unmarshal(data)

    #prepare next packet
    ntp.orig_timestamp=ntp.tx_timestamp
    ntp.recv_timestamp = rec
    
    data = ntp.marshal()
    ntp.tx_timestamp= time.time()
    sock.sendto(data,addr)