from socket import *
import threading
from time import sleep

class IPNotAvailable(Exception):
    def __init__(self):
        super().__init__('This IP is not available.')

PRIV_IP = '02'
USER_INFO = '03'
MSG = '04'

exit_signal = threading.Event() # thread exit flag
threads = [] # keep all threads and do .join() when the process terminates

sockets = {} # keep other users' socket

def create_TCP():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(('', 8080)) # always use 8080 port for hole punching
    return sock

def tryConnecting(ip, port):
    _sock = create_TCP()
    for i in range(0,3):
        try:
            print(str((ip,port)),' try')
            _sock.connect((ip, port))
            _sock.settimeout(0) # set .recv() timeout as 0 (non-blocking)
            sockets[(ip,port)] = _sock
            
            # success to connect to this user
            thread_user = threading.Thread(target = from_user, args = ((ip,port),))
            threads.append(thread_user)
            thread_user.start()
            return
        except Exception: # usually TimeoutError
            continue
    
    #Fail to connect
    _sock.close()
    raise IPNotAvailable


def connectToUsers(users_info):
    users_info = users_info.split('/')
    for idx in range(0, len(users_info)-1):
        user_info = users_info[idx]
        user = user_info.split(',') #user[0]: private IP, user[1]: public IP, user[2] : port
        port = int(user[2])
        try:
            tryConnecting(user[0],port) # try to connect to 'private' IP for a certain period of time
        except IPNotAvailable:
            try:
                tryConnecting(user[1],port) # try to connect to 'public' IP for a certain period of time
            except IPNotAvailable:
                print('Fail to connect to ', user_info)
                continue
        print('Success to connect to ', user_info)


# keep a connection to relay server
def from_relay(relaySock): 
    while not exit_signal.is_set():
        try:
            msg = relaySock.recv(1024).decode('utf-8')
            if(msg[0:2] == USER_INFO): # receive new user info
                con_user = threading.Thread(target = connectToUsers, args = (msg[2:],))
                threads.append(con_user)
                con_user.start()
        except BlockingIOError: # handle an asynchronous operation
            continue
        except Exception: # relay server is not available
            break
    relaySock.close()
    print('Relay thread terminated')

def from_user(addr):
    userSock = sockets[addr]
    while not exit_signal.is_set():
        try:
            msg = userSock.recv(1024).decode('utf-8')
            if(msg[0:2] == MSG): # receive message from this user 
                print(str(addr),' :', msg[2:])
        except BlockingIOError:
            continue
        except Exception:
            break
    userSock.close()
    del sockets[addr]
    print('User thread terminated')
        


#connect to relay server
relaySock = create_TCP()
try:
    relaySock.connect(('server IP', 8080))
    relaySock.settimeout(0) # make .recv() work as non-blocking
    print('Success to connect to Relay')
    relaySock.send((PRIV_IP + gethostbyname(gethostname())).encode('utf-8'))
    thread_relay = threading.Thread(target = from_relay, args = (relaySock,))
    thread_relay.start()

    while True:
        sendData = input('>>>')   
        if(sendData != 'exit'): 
            for socket in sockets.values():
                socket.send(('04'+sendData).encode('utf-8'))
        else: # if sendData == exit, then close this program
            exit_signal.set()

            thread_relay.join()
            for _thread in threads:
                _thread.join()

            print("Everything terminated well")
            break

except TimeoutError: # fail to connect to relay server
    relaySock.close()
    print('Relay server is not running')

 

