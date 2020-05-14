from socket import *
from time import sleep

# Message 1 byte Header
#PING = '00'
#PONG = '01'
PRIV_IP = '02'
USER_INFO = '03'

# keep users' socket and private IP
sockets = {}
priv_IPs = {}

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', 8080)) # use 8080 port
serverSock.listen()

while True:
    try:
        clientSock, addr = serverSock.accept()

        msg = clientSock.recv(1024).decode('utf-8') # receive user's private IP
        if(msg[0:2] == PRIV_IP):  # if header is fine
            print('new connection from ',str(addr))
            priv_IP = msg[2:]

            delete_list = []

            user_info_msg = USER_INFO # header
            for _addr in sockets:
                try:
                    # send new user's info to other users
                    sockets[_addr].send( (USER_INFO + priv_IP + ',' + addr[0] + ',' + str(addr[1]) + '/').encode('utf-8') ) 
                    # send current users' info to new user
                    user_info_msg += priv_IPs[_addr]+','+_addr[0]+','+str(_addr[1])+'/'  
                
                except Exception: # if this current user's socket is not available, append this to delete list
                    sockets[_addr].close()
                    delete_list.append(sockets[_addr])
            
            for sock in delete_list: # Prevent Runtime Error: dictionary changed size during iteration(above for statement)
                del sock

            try:
                if(user_info_msg != USER_INFO): # if user_info_msg == USER_INFO header, then it means there are no current users
                    print(user_info_msg) # for testing
                    clientSock.send(user_info_msg.encode('utf-8'))
                
                # register new member's socket and info to lists
                sockets[addr] = clientSock
                priv_IPs[addr] = priv_IP   

            except Exception: # if new member's socket is not available, close this socket
                clientSock.close()        

            

    except KeyboardInterrupt:
        # close every socket
        clientSock.close()
        for socket in sockets.values():
            socket.close()
        print("stop server")
        serverSock.close()
        break
        
    
    
