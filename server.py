import threading
import socket

class Server():
    def __init__(self, host, port):    
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.buffer = 64
        self.client_details = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)

    def send_message(self, conn, message):
        #fisrt of all we need to send size details
        message_size = str(len(message)).encode('utf-8')
        #procces message size details
        message_size += b' ' * (self.buffer - len(message_size))
        #send message size details
        conn.send(message_size)

        #then send the message
        conn.send(message.encode('utf-8'))

    def recv_message(self, conn):
        msg_size = conn.recv(self.buffer).decode('utf-8')
        # checking if msg is none or not if not proceed
        if msg_size:
            msg_size = int(msg_size) # this is the size of up comming message
            msg = conn.recv(msg_size).decode('utf-8') #recive and decode
            return msg #return message
        
        else:
            # return false if nothing recived
            # so we can check for it and call again
            return False

    def __handle_clients(self, conn, addr):
        while True: pass
        conn.close()

    def start_server(self):
        """
            DOCSTRING: this function will start the server.
            This server will accept many number of clients.
            for each client with a new thread.
        """
        #first of all start listening for the clients
        self.server.listen()
        print('[START] Server is online and live')

        # accpet infinit clients
        while True:
            #accept thread
            conn, addr = self.server.accept()
            #create thread for the client
            client_thread = threading.Thread(target=self.__handle_clients, args=(conn, addr))
            print(f'[CONNECTION] new connection from {addr[0]} | {addr[1]}')
            print(f'[DETAILS] now {threading.active_count()}(s) clients are online')

            #start thread
            client_thread.start()

            #now recive the client id from the client
            client_id = self.recv_message(conn)
            print(client_id)

            #add client details for the dictionary
            self.client_details[client_id] = [conn, addr]

        # kill the thread after loop exited
        client_thread.join()

server_instance = Server(socket.gethostbyname(socket.gethostname()), 5050)
server_instance.start_server()