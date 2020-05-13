from socket import *
from _thread import *
from timeout import timeout
from time import sleep
PING = '00'
PONG = '01'
PRIV_IP = '02'
USER_INFO = '03'

sockets = {}
priv_IPs = {}

@timeout(10)
def isUserAlive(addr): # idx : users array에서 user의 index
    socket = sockets[addr]
    try:
        socket.send(PING.encode('utf-8'))
        print('PING sent')
        data = socket.recv(1024)
        msg = data.decode('utf-8')
        if msg != PONG:
            raise Exception    
    except ConnectionResetError:
        raise Exception
    print('PONG came')

def PING_check(addr):
    while True:
        try:
            isUserAlive(addr)
            sleep(60) # 1분 주기로 ping 메세지 보냄
        except Exception:
            print(str(addr),' not alive')
            sockets[addr].close() # 소켓 종료
            del sockets[addr] # sockets dict에서 해당 소켓 삭제
            break

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', 8080))
serverSock.listen()

while True:
    try:
        clientSock, addr = serverSock.accept()
        print('new connection from ',str(addr))
        msg = clientSock.recv(1024).decode('utf-8')

        if(msg[0:2] == PRIV_IP): 
            # priv IP 등록
            priv_IP = msg[2:]
            print('priv IP info 도착')

            #새로운 유저에게 기존 유저 정보 전달
            user_info_msg = USER_INFO
            for _addr in sockets: # 기존 user들 정보를 새로운 user에게 전달함 , 기존 유저들에게 새로운 유저 정보도 전달함 -> hole punching 위함
                sockets[_addr].send( (USER_INFO + priv_IP + ',' + addr[0] + ',' + str(addr[1]) + '/').encode('utf-8') ) # user info format: 사설 IP,공인 IP,포트/
                user_info_msg += priv_IPs[_addr]+','+_addr[0]+','+str(_addr[1])+'/'  

            if(user_info_msg != USER_INFO):
                clientSock.send(user_info_msg.encode('utf-8'))
                print(user_info_msg)                

            # 새로운 유저 등록
            sockets[addr] = clientSock # 소켓 등록
            priv_IPs[addr] = priv_IP
            start_new_thread(PING_check, (addr,)) # PING PONG 체크 thread

    except KeyboardInterrupt:
        for socket in sockets:
            socket.close()
        print("stop server")
        break
    
serverSock.close()
    

