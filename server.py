# import modules
import socket
import threading
from time import sleep

# define constants
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'
ADDRESS = (SERVER, PORT)
HEADER = 64

#create an socket and bind it
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

def send_msg(conn, addr):
    while True:
        sleep(2)
        #message = input('send /#> ').strip()
        message = "yanawa yanna modayaaa.... bllllllllllllllll"
        print("[SEND] send msg to the client") # add a spacing
        #encodeing the message
        msg = message.encode(FORMAT)
        #set msg length
        msg_length = str(len(msg)).encode(FORMAT)
        msg_length += b' ' * (HEADER - len(msg_length))

        #sending the length data
        conn.send(msg_length)
        conn.send(msg)

def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} is online and live')
    send_m = threading.Thread(target=send_msg, args=(conn, addr))
    send_m.start()
    while True:
        msg_len = conn.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            message = conn.recv(msg_len).decode(FORMAT)
            if message == 'quit_conn()':
                print(f'[DISCONNECT] {addr} has been disconnected')
                break
            print(f'[MSG] from {addr} -> {message}')
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
