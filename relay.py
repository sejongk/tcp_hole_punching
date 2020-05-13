from socket import *
from time import sleep
PING = '00'
PONG = '01'
PRIV_IP = '02'
USER_INFO = '03'

sockets = {}
priv_IPs = {}

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', 8080))
serverSock.listen()

while True:
    try:
        clientSock, addr = serverSock.accept()

        msg = clientSock.recv(1024).decode('utf-8')
        if(msg[0:2] == PRIV_IP): 
            print('new connection from ',str(addr))
            priv_IP = msg[2:]

            delete_list = []

            #새로운 유저에게 기존 유저 정보 전달
            user_info_msg = USER_INFO
            for _addr in sockets: # 기존 user들 정보를 새로운 user에게 전달함 , 기존 유저들에게 새로운 유저 정보도 전달함 -> hole punching 위함
                try:
                    sockets[_addr].send( (USER_INFO + priv_IP + ',' + addr[0] + ',' + str(addr[1]) + '/').encode('utf-8') ) # user info format: 사설 IP,공인 IP,포트/
                    user_info_msg += priv_IPs[_addr]+','+_addr[0]+','+str(_addr[1])+'/'  
                
                except Exception:
                    print('connection Error occur 1')
                    sockets[_addr].close()
                    delete_list.append(sockets[_addr])
            
            for sock in delete_list: # for preventing Runtime Error: dictionary changed size during iteration
                del sock

            try:
                if(user_info_msg != USER_INFO):
                    print(user_info_msg)
                    clientSock.send(user_info_msg.encode('utf-8'))
                # 새로운 유저 등록
                sockets[addr] = clientSock
                priv_IPs[addr] = priv_IP   

            except Exception:
                print('connection Error occur 2')
                clientSock.close()        

            

    except KeyboardInterrupt:
        clientSock.close()
        for socket in sockets.values():
            socket.close()
        print("stop server")
        serverSock.close()
        break
        
    
    
