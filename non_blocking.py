from socket import *

sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.connect(('server IP', 8080))
sock.settimeout(0) # set this socket as non-blocking

 
while True:
    try:
        data = sock.recv(1024)
        msg = data.decode('utf-8')
        print('msg ',msg)
    except BlockingIOError:
        print('next')
        continue 
            
