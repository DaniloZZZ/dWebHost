import socket
import time

if __name__ == '__main__':
    UDP_IP = "192.168.0.1"
    UDP_PORT = 12345
    MESSAGE = "KEEP ALIVE"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while True:
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        time.sleep(2)
