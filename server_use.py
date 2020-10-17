# import modules
import socket
import threading

# define constants
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'
ADDRESS = (SERVER, PORT)
HEADER = 64

clients = {} #client data and their connections will append to this

#create an socket and bind it
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def send_msg(conn, addr, message = False):
    looper = True
    while looper:
        if not message: message = input('msg -> ').strip()
        else: looper = False

        print("[SEND] send msg to the client") # add a spacing
        #encodeing the message
        msg = message.encode(FORMAT)
        #set msg length
        msg_length = str(len(msg)).encode(FORMAT)
        msg_length += b' ' * (HEADER - len(msg_length))

        #sending the length data
        conn.send(msg_length)
        conn.send(msg)

def recv_msg(conn):
    msg_len = conn.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        message = conn.recv(msg_len).decode(FORMAT)
        if message == 'quit_conn()':
            return False
        else:
            return message
    else:
        return True        

def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} is online and live')
    isNewClient = True
    while True:
        if isNewClient:
            client_data = recv_msg(conn)
            clients[client_data] = [conn, addr]
            send_msg(conn, addr)
            isNewClient = False
            print(clients)
        else:
            message = recv_msg(conn)
            if message: print(f'[MSG] message recived from <- {addr[0]}')
            else: break

    print(f'[DISCONNECT] client {addr[0]} disconnected')
    conn.close()

def main():
    server.listen()
    print(f'[LISTENING] server is listening on {SERVER} | {PORT}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount()-1} are online')
        

########### BEING THE MAIN PROGRAM #############
if __name__ == '__main__':
    print('[STARTING] The server is starting ...')
    main()
