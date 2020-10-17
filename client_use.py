import socket
import threading
from time import sleep

# define constants
PORT = 5050
FORMAT = 'utf-8'
HEADER = 64
SERVER = input("Server Addr -> ").strip()
ADDRESS = (SERVER, PORT)
CLIENT_ID = 'yasiru'

def send_msg(message = None):
    to_loop = True
    while to_loop:
        if message == None: message = input('send /#> ').strip()
        else: to_loop = False
        #encodeing the message
        msg = message.encode(FORMAT)
        #set msg length
        msg_length = str(len(msg)).encode(FORMAT)
        msg_length += b' ' * (HEADER - len(msg_length))

        #sending the length data
        client.send(msg_length)
        client.send(msg)
        message = None
        print() # add a spacing

        if message == 'quit_conn()':
            break

def recv_msg(client, once = False):
    try:
        while not once:
            msg_len = client.recv(HEADER).decode(FORMAT)
            
            if msg_len:
                msg_len = int(msg_len)
                message = client.recv(msg_len).decode(FORMAT)
                if not once: print(f'[RECIVED] #> {message}')
                else: return message
    except ValueError:
        pass


# create client and bind to the
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)

# send client data
send_msg(CLIENT_ID)
while True:
    connect_status = recv_msg(client, once=True)
    if connect_status != None:
        print(connect_status)
        break

sending_thread = threading.Thread(target=send_msg)
receving_thread = threading.Thread(target=recv_msg , args=(client))

#starting threads
sending_thread.start()
receving_thread.start()
#killing threads
#sending_thread.join()
#receving_thread.join()