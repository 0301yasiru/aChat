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

    def __hidden_send(self,conn, client_id):
        while True:
            # check if crrent client has messages in queu
            # if then forward it to them
            if len(self.client_details[client_id][2]):
                message = self.client_details[client_id][2].pop(0)
                self.send_message(conn, message)
                print(f'[FORWARD] msg forwarded to -> {client_id}')

    def __hidden_recv(self, conn, client_id):
        while True:
            # firstly recive the message
            message = self.recv_message(conn)
            # then check if that is a command if not procees
            if not self.__run_commands(message, conn, client_id):
                print(f'[RECIVED] msg recived from -> {client_id}')
                # put that message in the partners message queue
                partner = self.client_details[client_id][1][0]
                self.client_details[partner][2].append(message)

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
            return ""

    def __run_commands(self, message, conn, client_id):
        #split the message from spaces
        message = message.strip().split()
        commands = ['connect']
        
        try:
            if message[0] in commands:

                if message[0] == 'connect':
                    # chech if requested client online and live
                    if message[1] in self.client_details:
                        #check if requested client already bound
                        if not len(self.client_details[message[1]][1]):
                            self.client_details[message[1]][1].append(client_id)
                            self.client_details[client_id][1].append(message[1])

                            self.client_details[message[1]][2].append(f'[+] You are connected to -> {client_id}')
                            self.client_details[client_id][2].append(f'[+] You are connected to -> {message[1]}')

                        else:
                            self.send_message(conn, '[-] Requested client already bounded')
                    else:
                        self.send_message(conn, '[-] Requested client is not online')

                return True
            else:
                return False

        except IndexError:
            return False

    def __handle_clients(self, conn, addr, client_id):
        # waiting for client to pair
        while not self.client_details[client_id][1]:
            self.__run_commands(self.recv_message(conn), conn, client_id)
            
        # create threads for recive messages and send messages
        reciving_thread = threading.Thread(target=self.__hidden_recv, args=(conn, client_id))
        sending_thread = threading.Thread(target=self.__hidden_send, args=(conn, client_id))

        # start threads
        reciving_thread.start()
        sending_thread.start()

        # after disconnecting kill those threads
        reciving_thread.join()
        sending_thread.join()

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
            print(f'[CONNECTION] new connection from {addr[0]} | {addr[1]}')
            print(f'[DETAILS] now {threading.active_count()}(s) clients are online')

            #now recive the client id from the client
            client_id = self.recv_message(conn)
            print(client_id)

            #add client details for the dictionary
            self.client_details[client_id] = [conn, [], []]

            #create thread for the client
            client_thread = threading.Thread(target=self.__handle_clients, args=(conn, addr, client_id))
            #start thread
            client_thread.start()

        # kill the thread after loop exited
        client_thread.join()

server_instance = Server(socket.gethostbyname(socket.gethostname()), 5050)
server_instance.start_server()
