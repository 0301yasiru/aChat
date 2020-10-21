# !/usr/bin/python
# programmed by Yasiru Senerath
# this is the script for the server

import threading
import socket
from random import randint
from sys import exit
from time import sleep
from datetime import datetime
from datetime import date
import multiprocessing

class Server():
    def __init__(self, host, port):    
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.buffer = 64
        self.client_details = {}

        self.error_log = '' # to be initialized
        self.server_log = '' # to be initialized

        # in client details the details of client will be saved as follow
        # key- client_id
        # client_id : [conn, [parter], [messages,]]

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)

        self.terminate = False

    def __eject_client(self, client_id):
        """
        DOCSTRING: this function will cleanly remove a connected client
        means this will remove all the record fromclient data closing the connection

        client_id: user name of the client
        """
        try:
            #firtly remove the connection from the other user
            partner_id = self.client_details[client_id][1][0]
            self.client_details[partner_id][1].clear()
            self.client_details[partner_id][2].clear()
            #secondly delete the current session of the client
            del(self.client_details[client_id])
            print('[EJECT] client ejcted -> {}'.format(client_id))
            self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.server_log.write('[EJECT] client ejcted -> {}\n'.format(client_id))
        except IndexError as err:
            self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.error_log.write('[INDEXERR] err msg -> {}\n'.format(err))

    def __hidden_send(self,conn, client_id):
        """
        DOCSTRING: this is the function which uses by the thread to forward
        messages
        conn: connection of the client
        client_id: user name of the client
        """
        # if the reject function removes client from the client list
        # this function must be terminated to check whether id in the list
        while (client_id in self.client_details) and (not self.terminate):
            # check if crrent client has messages in queu
            # if then forward it to them
            if len(self.client_details[client_id][2]):
                message = self.client_details[client_id][2].pop(0)
                self.send_message(conn, message, client_id)
                print(f'[FORWARD] msg forwarded to -> {client_id}')
                self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.server_log.write(f'[FORWARD] msg forwarded to -> {client_id}\n')

    def __hidden_recv(self, conn, client_id):
        """
        DOCSTRING: this is the function which uses by the thread to recevie messages
        conn: connection of the client
        client_id: user name of the client
        """
        # if the reject function removes client from the client list
        # this function must be terminated to check whether id in the list
        while (client_id in self.client_details) and (not self.terminate):
            # firstly recive the message
            message = self.recv_message(conn, client_id)
            # check if the message is a none type then do not proceed
            if message:
                # then check if that is a command if not procees
                if not self.__run_commands(message, conn, client_id):
                    print(f'[RECIVED] msg recived from -> {client_id}')
                    self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                    self.server_log.write(f'[RECIVED] msg recived from -> {client_id}\n')
                    # put that message in the partners message queue
                    partner = self.client_details[client_id][1][0]
                    self.client_details[partner][2].append(message)

    def send_message(self, conn, message, client_id):
        """
        DOCSTRING: this is the primary function to sent messages anyway
        conn: connection of the client
        message: the message as an string
        client_id: user name of the client
        """
        try:
            #fisrt of all we need to send size details
            message_size = str(len(message)).encode('utf-8')
            #procces message size details
            message_size += b' ' * (self.buffer - len(message_size))
            #send message size details
            conn.send(message_size)
            #then send the message
            conn.send(message.encode('utf-8'))
        
        # and OS error may be occure if non socket object interaced
        except OSError as err:
            print('[OSERROR] error msg -> {}'.format(err))
            self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.error_log.write('[OSERROR] error msg -> {}\n'.format(err))

    def recv_message(self, conn, client_id=None):
        """
        DOCSTRING: this is the primary function to receve messages
        conn: connection of the client
        client_id: user name of the client (this info will use to eject client)
        """
        # recv method will wait until it receves a messgae if not will not continue
        # in order to propper working code must continue so, it will stop waiting 
        # after 2 seconts it will continue the code
        conn.settimeout(2)
        try:
            # receive the size of the message
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
        
        # if the client close the connection fource fully this error will occure
        # then we should remove the client from the reords so eject
        except ConnectionResetError as err:
            print('[CONRESETERROR] error msg -> {}'.format(err))
            self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.error_log.write('[CONRESETERROR] error msg -> {}\n'.format(err))

            conn.settimeout(None)
            self.__eject_client(client_id)
            return False
    
        # if time out or non socket will rais this error
        except OSError as err:
            if str(err) == 'timed out': 
                conn.settimeout(None)
            else: 
                print('[OSERROR] error msg -> {}'.format(err))
                self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.error_log.write('[OSERROR] error msg -> {}\n'.format(err))

    def __run_commands(self, message, conn, client_id):
        """
        DOCSTRING: this is the primary function to run command received by the message
        all the recived message will come to this place first to check is this is a command.
        if a command it will executed and will not display to the client.

        IMPORTANT: If the checket message is a command we should return a True statement

        conn: connection of the client
        clinet_id: user name of the client
        message: message to be checked
        """
        #split the message from spaces
        try:
            conn.settimeout(None)
            message = message.strip().split()
        except AttributeError as err:
            self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.error_log.write('[ATTRERROR] error msg -> {}\n'.format(err))
            return False
        
        try:
            # the connect command will bind teo client together, so they cantalk to ech other
            if message[0] == 'connect':
                # chech if requested client online and live
                if message[1] in self.client_details:
                    #check if requested client already bound
                    if not len(self.client_details[message[1]][1]):
                        self.client_details[message[1]][1].append(client_id)
                        self.client_details[client_id][1].append(message[1])

                        # sentd the connection status for booth clients
                        self.client_details[message[1]][2] = [f'You are connected to -> {client_id}']
                        self.client_details[client_id][2]  = [f'You are connected to -> {message[1]}']
                        print('[BINDED] {} and {} are binded'.format(client_id, message[1]))
                        self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                        self.server_log.write('[BINDED] {} and {} are binded\n'.format(client_id, message[1]))

                    else:
                        self.send_message(conn, '[-] Requested client already bounded', client_id)
                else:
                    self.send_message(conn, '[-] Requested client is not online', client_id)
                return True

            # the quiting message. if this message recived eject the client
            elif message[0] == 'conn_quit()':
                self.__eject_client(client_id)
                return True

            # if not a command retun false
            else:
                return False

        except IndexError as err:
            self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.error_log.write('[INDEXERR] error msg -> {}\n'.format(err))
            return False

    def __handle_clients(self, conn, addr, client_id):
        """
        DOCSTRING: this is the function used by the each thread for each client
        conn: connection of the client
        addr: ip and port combination of the client
        client_id: user name of the client
        """
        
        # this variable will used to switch if client forcefully clise the connection
        # even before the bind of another client

        client_aborted = False

        # until a the user have and partner we cannot gofurther. the client must have an partner
        # to chat with. so wait until client recive and partne id

        while (not self.client_details[client_id][1]) and (not self.terminate) :
            # recive messgae
            message = self.recv_message(conn, client_id)
            if message:
                self.__run_commands(message, conn, client_id)

            # if message is false connection reset error must be occured. means forcefully
            # closed the connection. so abort the procedure and eject the client
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

    def __main_server_start(self):
        """
            DOCSTRING: this function will start the server.
            This server will accept many number of clients.
            for each client with a new thread.
        """
        #first of all start listening for the clients
        self.server.listen()

        print('[START] Server is online and live')
        self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
        self.server_log.write('[START] Server is online and live')

        # accpet infinit clients
        while not self.terminate:
            #accept thread
            conn, addr = self.server.accept()
            #now recive the client id from the client
            client_id = self.recv_message(conn)

            print(f'[CONNECTION] new connection from {addr[0]} | {addr[1]} | {client_id}')
            print(f'[DETAILS] now {threading.active_count()}(s) clients are online')
            self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.server_log.write(f'[CONNECTION] new connection from {addr[0]} | {addr[1]} | {client_id}\n')

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

    def __main_master_input(self):
        """
        DOCSTRING: this is the main function that allows to run various commands on the server
        for example list down clients, shut down the server, restart the server
        """
        while True:
            # wait for the input from the user
            command = input().strip()
            # if command is the power off
            if command == 'poweroff':
                # set master shut down
                print('[SHUTDOWN] The server is shutting down in 10s .', end='')
                for _ in range (10):
                    sleep(1)
                    print(' .', end='')

                self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.server_log.write('[SHUTDOWN] The server is shutting down\n')
                self.terminate = True
                break
        
        #close the opened log files
        self.server_log.close()
        self.error_log.close()
        # after waiting the system must be terminated
        exit(0)

    def start_server(self):
        """
        DOCSTRING: the function of this function is simple, create two proccess for the server
        start function and main input function and run it
        """
        # fisrt of all create two files for the server and error logging
        prefix = 'logs\\' + str(date.today()) + '__' + str(datetime.now().strftime('%H_%M_'))
        self.error_log = open(prefix + 'error_log.txt', 'w')
        self.server_log = open(prefix + 'server_log.txt', 'w')

        # firstly create two thread for the input and main server start
        # server_start = threading.Thread(target=self.__main_server_start)
        # master_input = threading.Thread(target=self.__main_master_input)
        
        server_start = multiprocessing.Process(target=self.__main_server_start)
        master_input = multiprocessing.Process(target=self.__main_master_input)

        # start both threads
        server_start.start()
        master_input.start()

        #join both threads
        server_start.join()
        master_input.join()
        
        #double check for log file closing
        self.server_log.close()
        self.error_log.close()


if __name__ == '__main__':
    server_instance = Server('192.168.1.2', 5151)
    server_instance.start_server()
