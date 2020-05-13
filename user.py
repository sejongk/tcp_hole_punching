from socket import *
import threading
from time import sleep

PING = '00'
PONG = '01'
PRIV_IP = '02'
USER_INFO = '03'
MSG = '04'

exit_signal = threading.Event()
threads = []

sockets = {}

def create_TCP():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(('', 8080))
    return sock

def tryConnecting(ip, port):
    _sock = create_TCP()
    for i in range(0,3):
        try:
            print(str((ip,port)),' try')
            _sock.connect((ip, port))
            sockets[(ip,port)] = _sock

            thread_user = threading.Thread(target = from_user, args = ((ip,port),))
            threads.append(thread_user)
            thread_user.start()
            return
        except Exception:
            continue

    _sock.close()
    raise Exception


def connectToUsers(users_info):
    users_info = users_info.split('/')
    for idx in range(0, len(users_info)-1):
        user_info = users_info[idx]
        user = user_info.split(',') #user[0]: private IP, user[1]: public IP, user[2] : port
        port = int(user[2])
        try:
            tryConnecting(user[0],port)# 일정 시간 동안 사설 IP로 연결 시도
        except Exception:
            try:
                tryConnecting(user[1],port)# 일정 시간 동안 공인 IP로 연결 시도
            except Exception:
                print('Fail to connect to ', user_info)
                continue
        print('Success to connect to ', user_info)


def from_relay(relaySock):
    while not exit_signal.is_set():
        try:
            msg = relaySock.recv(1024).decode('utf-8')
            
            if(msg[0:2] == USER_INFO):
                con_user = threading.Thread(target = connectToUsers, args = (msg[2:],))
                threads.append(con_user)
                con_user.start()

        except Exception:
            break
    relaySock.close()
    print('from relay off')

def from_user(addr):
    userSock = sockets[addr]
    while not exit_signal.is_set():
        try:
            msg = userSock.recv(1024).decode('utf-8')
            if(msg[0:2] == MSG):
                print(str(addr),' :', msg[2:])
        except Exception:
            break
    userSock.close()
    del sockets[addr]
    print('from_user off')
        


#relay server와 연결
relaySock = create_TCP()
try:
    relaySock.connect(('123.248.99.41', 8080))
    print('Success to connect to Relay')
    relaySock.send((PRIV_IP + gethostbyname(gethostname())).encode('utf-8'))
    thread_relay = threading.Thread(target = from_relay, args = (relaySock,)) # relay server부터로의 메세지에 대한 response
    thread_relay.start()

    while True:
        sendData = input('>>>')   
        if(sendData != 'exit'):
            for socket in sockets.values():
                socket.send(('04'+sendData).encode('utf-8'))
        else:
            exit_signal.set()

            thread_relay.join()
            for _thread in threads:
                _thread.join()

            print("Everything terminates well")
            break

except TimeoutError:
    relaySock.close()
    print('Relay server is not running')


'''


try:
            sendData = input('>>>')   
            for socket in sockets.values():
                socket.send(('04'+sendData).encode('utf-8'))

        except KeyboardInterrupt:
            exit_signal.set()
            for socket in sockets.values():
                    socket.close()
            relaySock.close()

            thread_relay.join()
            for _thread in threads:
                _thread.join()

            print("stop all connections")
            break
'''



 

