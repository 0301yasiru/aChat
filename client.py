import socket
import threading

# define constants
PORT = 5050
FORMAT = 'utf-8'
HEADER = 64
SERVER = input("Server Addr -> ").strip()
ADDRESS = (SERVER, PORT)

# create client and bind to the
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

def send_msg():
    while True:
        message = input('send /#> ').strip()
        print() # add a spacing
        #encodeing the message
        msg = message.encode(FORMAT)
        #set msg length
        msg_length = str(len(msg)).encode(FORMAT)
        msg_length += b' ' * (HEADER - len(msg_length))

        #sending the length data
        client.send(msg_length)
        client.send(msg)

def recv_msg():
    while True:
        msg_len = client.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            message = client.recv(msg_len).decode(FORMAT)
            print(f'[RECIVED] #> {message}')

sending_thread = threading.Thread(target=send_msg)
receving_thread = threading.Thread(target=recv_msg)

#starting threads
sending_thread.start()
receving_thread.start()
#killing threads
sending_thread.join()
receving_thread.join()