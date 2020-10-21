# !/usr/bin/python
# programmed by Yasiru Senerath
# this is the script for the server

import threading
import socket

class Server():
    def __init__(self, host, port):    
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.buffer = 64
        self.client_details = {}

        # in client details the details of client will be saved as follow
        # key- client_id
        # client_id : [conn, [parter], [messages,]]

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)

    def __eject_client(self, client_id):
        try:
            #firtly remove the connection from the other user
            partner_id = self.client_details[client_id][1][0]
            self.client_details[partner_id][1].clear()
            self.client_details[partner_id][2].clear()
            #secondly delete the current session of the client
            del(self.client_details[client_id])
            print('[EJECT] client ejcted -> {}'.format(client_id))
        except IndexError:
            pass

    def __hidden_send(self,conn, client_id):
        while client_id in self.client_details:
            # check if crrent client has messages in queu
            # if then forward it to them
            if len(self.client_details[client_id][2]):
                message = self.client_details[client_id][2].pop(0)
                self.send_message(conn, message, client_id)
                print(f'[FORWARD] msg forwarded to -> {client_id}')

    def __hidden_recv(self, conn, client_id):
        while client_id in self.client_details:
            # firstly recive the message
            message = self.recv_message(conn, client_id)
            # check if the message is a none type then do not proceed
            if message:
                # then check if that is a command if not procees
                if not self.__run_commands(message, conn, client_id):
                    print(f'[RECIVED] msg recived from -> {client_id}')
                    # put that message in the partners message queue
                    partner = self.client_details[client_id][1][0]
                    self.client_details[partner][2].append(message)

    def send_message(self, conn, message, client_id):
        try:
            #fisrt of all we need to send size details
            message_size = str(len(message)).encode('utf-8')
            #procces message size details
            message_size += b' ' * (self.buffer - len(message_size))
            #send message size details
            conn.send(message_size)
            #then send the message
            conn.send(message.encode('utf-8'))
        
        except OSError as err:
            print('[OSERROR] error msg -> {}'.format(err))

    def recv_message(self, conn, client_id=None):
        conn.settimeout(2)
        try:
            msg_size = conn.recv(self.buffer).decode('utf-8')
            # undo time out after this line
            conn.settimeout(None)
            # checking if msg is none or not if not proceed
            if msg_size:
                msg_size = int(msg_size) # this is the size of up comming message
                msg = conn.recv(msg_size).decode('utf-8') #recive and decode
                return msg #return message
            else:
                # return false if nothing recived
                # so we can check for it and call again
                return ""

            conn.settimeout(None)
        
        except ConnectionResetError as err:
            print('[CONRESETERROR] error msg -> {}'.format(err))
            conn.settimeout(None)
            self.__eject_client(client_id)
            return False
    
        except OSError as err:
            if str(err) == 'timed out': conn.settimeout(None)
            else: print('[OSERROR] error msg -> {}'.format(err))

    def __run_commands(self, message, conn, client_id):
        #split the message from spaces
        try:
            conn.settimeout(None)
            message = message.strip().split()
        except AttributeError:
            return False

        commands = ['connect', 'conn_quit()']
        
        try:
            if message[0] in commands:

                if message[0] == 'connect':
                    # chech if requested client online and live
                    if message[1] in self.client_details:
                        #check if requested client already bound
                        if not len(self.client_details[message[1]][1]):
                            self.client_details[message[1]][1].append(client_id)
                            self.client_details[client_id][1].append(message[1])

                            self.client_details[message[1]][2] = [f'You are connected to -> {client_id}', 'bello']
                            self.client_details[client_id][2]  = [f'You are connected to -> {message[1]}', 'bello']
                            print('[BINDED] {} and {} are binded'.format(client_id, message[1]))

                        else:
                            self.send_message(conn, '[-] Requested client already bounded', client_id)
                    else:
                        self.send_message(conn, '[-] Requested client is not online', client_id)
                    return True

                elif message[0] == 'conn_quit()':
                    self.__eject_client(client_id)
                    return True

            else:
                return False

        except IndexError:
            return False

    def __handle_clients(self, conn, addr, client_id):
        # waiting for client to pair
        client_aborted = False

        while not self.client_details[client_id][1]:
            message = self.recv_message(conn, client_id)
            if message:
                self.__run_commands(message, conn, client_id)
            elif message == False:
                client_aborted = True
                del(self.client_details[client_id])
                break
        
        if not client_aborted:
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
            #now recive the client id from the client
            client_id = self.recv_message(conn)

            print(f'[CONNECTION] new connection from {addr[0]} | {addr[1]} | {client_id}')
            print(f'[DETAILS] now {threading.active_count()}(s) clients are online')

            #add client details for the dictionary
            self.client_details[client_id] = [conn, [], []]
            #create thread for the client
            client_thread = threading.Thread(target=self.__handle_clients, args=(conn, addr, client_id))
            #start thread
            client_thread.start()

        # kill the thread after loop exited
        client_thread.join()
        # close the connection
        conn.close()

server_instance = Server('192.168.1.2', 5151)
server_instance.start_server()
