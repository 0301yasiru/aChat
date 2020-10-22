import socket
import threading
from colors import COLORS
from platform import system

class Client():
    def __init__(self, client_id, server, port):
        self.buffer = 64
        self.client_id = client_id
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)

        # create the socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(2)

        self.terminate = False

        self.c = COLORS()

    def __hidden_send(self):
        while not self.terminate:
            try:
                current_msg = input().strip()
                if current_msg == 'conn_quit()':
                    self.terminate =True

                self.send_message(current_msg)
                print()

            except EOFError:
                exit()

    def __hidden_recv(self):
        while not self.terminate:
            message = self.recv_message()
            if message:
                print(self.c.Cyan + f'[RECIVED] {message}' + self.c.RESET)

    def send_message(self, message):
        #fisrt of all we need to send size details
        message_size = str(len(message)).encode('utf-8')
        #procces message size details
        message_size += b' ' * (self.buffer - len(message_size))
        #send message size details
        self.client.send(message_size)

        #then send the message
        self.client.send(message.encode('utf-8'))

    def recv_message(self):
        try:
            msg_size = self.client.recv(self.buffer).decode('utf-8')
            # checking if msg is none or not if not proceed
            if msg_size:
                msg_size = int(msg_size) # this is the size of up comming message
                msg = self.client.recv(msg_size).decode('utf-8') #recive and decode
                return msg #return message
            
            else:
                # return false if nothing recived
                # so we can check for it and call again
                return False

        except ConnectionResetError:
            exit()

        except OSError:
            # this error occure wen time out
            return False

    def __handle_client(self):
        # create threads for recive messages and send messages
        reciving_thread = threading.Thread(target=self.__hidden_recv)
        sending_thread = threading.Thread(target=self.__hidden_send)

        # start threads
        reciving_thread.start()
        sending_thread.start()

        # after disconnecting kill those threads
        reciving_thread.join()
        sending_thread.join()

    def start_client(self):
        """
            DOCSTRING: this function will start the server
            fisrt try to connect to the server. And if sccueed
            send client data and establish the connection
        """
        try:
            # connect to the server in order to start the client
            self.client.connect(self.addr)
            # send client data
            self.send_message(self.client_id)
            self.__handle_client()

        except ConnectionRefusedError:
            print("[ERROR] Server is Down program quiting")
            exit(0)
        
        except ConnectionAbortedError:
            print("[ERROR] Server aborted the connection")
            exit(0)

        except ConnectionError:
            print("[ERROR] Connection error")
            exit(0)


def read_conf_file():
    with open('client.conf', 'r') as config_file:
        config_data = config_file.readlines()

    client_conf_data = {}

    for line in config_data:
        line = line.split()
        client_conf_data[line[0]] = line[1:]

    return client_conf_data

conf_data = read_conf_file()

client_instance = Client(conf_data['client_id:'][0], conf_data['host:'][0], int(conf_data['port:'][0]))
client_instance.start_client()