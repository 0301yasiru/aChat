import socket
import threading

class Client():
    def __init__(self, client_id, server, port):
        self.buffer = 64
        self.client_id = client_id
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)

        # create the socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

        except ConnectionRefusedError:
            print("[ERROR] Server is Down program quiting")
            exit(0)
        
        except ConnectionAbortedError:
            print("[ERROR] Server aborted the connection")
            exit(0)

        except ConnectionError:
            print("[ERROR] Connection error")
            exit(0)

client_instance = Client('0301yasiru', '192.168.56.1', 5050)
client_instance.start_client()