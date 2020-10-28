# !/usr/bin/python
# programmed by Yasiru Senerath
# this is the script for the server

from libs.colors import COLORS
from time import sleep
from datetime import datetime
from datetime import date
from os import system
import threading
import socket
import platform

#create and global instance for the coloring puspose
c = COLORS()

class Server():
    def __init__(self, host, port, balcklist):    
        self.host = host
        self.port = int(port)
        self.addr = (self.host, self.port)
        self.buffer = 64
        self.client_details = {}
        self.balcklist = []

        self.error_log = '' # to be initialized
        self.server_log = '' # to be initialized

        # in client details the details of client will be saved as follow
        # key- client_id
        # client_id : [conn, [parter], [messages,]]

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)
        self.server.settimeout(5)

        self.terminate = False

    def __eject_client(self, client_id):
        """
        DOCSTRING: this function will cleanly remove a connected client
        means this will remove all the record fromclient data closing the connection

        client_id: user name of the client
        """
        try:
            # an key erroro may be occured when unbinded client force fully closed the connection
            # in thar case only remove that client and dont bother with partner
            try:
                #firtly remove the connection from the other user
                partner_id = self.client_details[client_id][1][0]
                self.client_details[partner_id][1][0] = None
                self.client_details[partner_id][2].clear()
                # and send the eject message to the partnet
                self.send_message(self.client_details[partner_id][0], '[!]connection is over', partner_id)

            except KeyError as err:
                self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.error_log.write('[KEYERROR] error msg -> {}\n'.format(err))

            #secondly delete the current session of the client
            del(self.client_details[client_id])
            print(c.Red+c.BOLD+'[EJECT]'+c.RESET+c.Red+' client ejcted -> {}'.format(client_id), c.RESET)
            self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.server_log.write('[EJECT] client ejcted -> {}\n'.format(client_id))
        except IndexError as err:
            self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
            self.error_log.write('[INDEXERR] error msg -> {}\n'.format(err))

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

            # though we checked client id in self.client_details stil it can be occure erorors
            # to expect an key error
            try:
                # first of all check if other client terminated the connection
                if self.client_details[client_id][1][0] == None:
                    break
                else:
                    if len(self.client_details[client_id][2]):
                        message = self.client_details[client_id][2].pop(0)
                        self.send_message(conn, message, client_id)
                        print(f'{c.BOLD}[FORWARD]{c.RESET} msg forwarded to -> {c.ULINE+client_id+c.RESET}')
                        self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                        self.server_log.write(f'[FORWARD] msg forwarded to -> {client_id}\n')

            except KeyError as err:
                self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.error_log.write(f'[KEYERROR] error message -> {err}\n')
                break

    def __hidden_recv(self, conn, client_id):
        """
        DOCSTRING: this is the function which uses by the thread to recevie messages
        conn: connection of the client
        client_id: user name of the client
        """
        # if the reject function removes client from the client list
        # this function must be terminated to check whether id in the list
        while (client_id in self.client_details) and (not self.terminate):
            # check if the other client ended the connection
            if self.client_details[client_id][1][0] == None:
                break
            else:
                # firstly recive the message
                message = self.recv_message(conn, client_id)
                # check if the message is a none type then do not proceed
                if message:
                    # then check if that is a command if not procees
                    if not self.__run_commands(message, conn, client_id):
                        print(f'{c.BOLD}[RECIVED]{c.RESET} msg recived from -> {c.ULINE+client_id+c.RESET}')
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
            print(c.Magenta+c.BOLD+'[OSERROR]'+c.RESET+c.Magenta, 'error msg -> {}'.format(err), c.RESET)
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
            # in this case unicode decode error may be occured
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
            
            except UnicodeDecodeError as err:
                print(f'{c.Magenta+c.BOLD}[UNICODEERROR]{c.RESET+ c.Magenta} error msg -> {err}')
                self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.error_log.write(f'[UNICODEERROR] error msg -> {err}\n')


            conn.settimeout(None)
        
        # if the client close the connection fource fully this error will occure
        # then we should remove the client from the reords so eject
        except ConnectionResetError as err:
            print(c.Magenta+c.BOLD+'[CONRESETERROR]'+c.RESET+ c.Magenta,'error msg -> {}'.format(err), c.RESET)
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
                print(c.Magenta+ c.BOLD+ '[OSERROR]'+ c.RESET+ c.Magenta, 'error msg -> {}'.format(err), c.RESET)
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
                # you cannot connect your self
                if message[1] != client_id:
                    # chech if requested client online and live
                    if message[1] in self.client_details:
                        #check if requested client already bound
                        if self.client_details[message[1]][1] != None:
                            self.client_details[message[1]][1][0] = client_id
                            self.client_details[client_id][1][0] = message[1]

                            # sentd the connection status for booth clients
                            self.client_details[message[1]][2] = [f'You are connected to -> {client_id}']
                            self.client_details[client_id][2]  = [f'You are connected to -> {message[1]}']
                            print(c.Green+c.BOLD+'[BINDED]{}{} {} and {} are binded'.format(c.RESET, c.Green,c.ULINE + client_id + c.RESET + c.Green,c.ULINE + message[1] + c.RESET + c.Green), c.RESET)
                            self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                            self.server_log.write('[BINDED] {} and {} are binded\n'.format(client_id, message[1]))
                        else:
                            self.send_message(conn, '[-] Requested client already bounded', client_id)
                    else:
                        self.send_message(conn, '[-] Requested client is not online', client_id)
                else:
                    self.send_message(conn, '[-] You cannot connect your self', client_id)
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
        # this main loop holds the client even avter their connection is over with othre client
        while not self.terminate:
            # this variable will used to switch if client forcefully clise the connection
            # even before the bind of another client

            client_aborted = False

            # until a the user have and partner we cannot gofurther. the client must have an partner
            # to chat with. so wait until client recive and partne id

            #fisrt of all check if this client exists.(if this client quited the connection)
            try:
                while (self.client_details[client_id][1][0] == None) and (not self.terminate) :
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
                
                else:
                    # else the main loop also must be brocken
                    break

            except KeyError as err:
                # if client closet their terminal quit the connection
                self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.error_log.write('[KEYERROR] error msg -> {}\n'.format(err))
                break

    def __main_server_start(self):
        """
            DOCSTRING: this function will start the server.
            This server will accept many number of clients.
            for each client with a new thread.
        """
        #first of all start listening for the clients
        self.server.listen()

        print(c.Green+c.BOLD+'[START]' + c.RESET + c.Green + 'Server is online and live {} | {}'.format(c.ULINE + self.host, str(self.port) + c.RESET))
        self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
        self.server_log.write('[START] Server is online and live {} | {}\n'.format(self.host, self.port))

        # accpet infinit clients
        while not self.terminate:
            try:
                #accept thread
                conn, addr = self.server.accept()
                #now recive the client id from the client
                client_id = self.recv_message(conn)

                # check if the client in the blacklist
                if client_id not in self.balcklist:
                    print(f'{c.Green+c.BOLD}[CONNECTION]{c.RESET+c.Green} new connection from {c.ULINE+addr[0]} | {addr[1]} | {client_id+c.RESET}')
                    self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                    self.server_log.write(f'[CONNECTION] new connection from {addr[0]} | {addr[1]} | {client_id}\n')

                    #add client details for the dictionary
                    self.client_details[client_id] = [conn, [None], []]
                    print(f'{c.Green+c.BOLD}[DETAILS]{c.RESET+c.Green} now {len(self.client_details)}(s) clients are online', c.RESET)
                    #create thread for the client
                    client_thread = threading.Thread(target=self.__handle_clients, args=(conn, addr, client_id))
                    #start thread
                    client_thread.start()
            
            except OSError as err:
                if str(err) != 'timed out':
                    print(c.Magenta+c.BOLD+'[OSERROR]'+c.RESET+c.Magenta, 'error msg -> {}'.format(err), c.RESET)
                    self.error_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                    self.error_log.write('[OSERROR] error msg -> {}\n'.format(err))

        try:
            # close the connection
            conn.close()
            # kill the thread after loop exited
            client_thread.join()

        except UnboundLocalError:
            # this error may be occur if the server sutsdown even before one client onnect
            pass
            
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
                print(c.Cyan+c.BOLD+'[SHUTDOWN]',c.RESET, c.Cyan,'The server is shutting down',c.RESET, end='')

                self.server_log.write(datetime.now().strftime("%H:%M:%S ==> "))
                self.server_log.write('[SHUTDOWN] The server is shutting down\n')
                self.terminate = True
                break

            elif command == 'help':
                with open('libs\\help_server_module.txt', 'r') as help_file:
                    print(help_file.read(), end='\n\n\n')

            elif command == 'list_clients' or command == 'clients':
                # in this case value error may occure if no clients exists
                try:

                    # firstly get client ids
                    client_ids = list(self.client_details.keys())
                    client_ids.insert(0, 'U_NAME')
                    # then get client keys
                    client_vals = self.client_details.values()
                    # client addrs and partnets from the values
                    client_combination = [(item[0].getpeername(), item[1][0]) for item in client_vals]
                    # we dont need vals any moe delete it from the ram
                    del(client_vals)
                    # devide addresses and partner names
                    client_addr, client_part = zip(*client_combination)
                    client_part = list(client_part)
                    client_part.insert(0, 'PARTNER')
                    client_part = list(map(str, client_part))
                    # dlete the client combination
                    del(client_combination)
                    # devide ips and ports from the addrs
                    client_ips, client_ports = map(list, zip(*client_addr))
                    client_ips.insert(0, 'IP ADDR')
                    client_ports.insert(0, 'PORT')
                    # delete client address
                    del(client_addr)

                    # form the size table
                    sizes = [max(map(lambda item : len(item), client_ids)) + 2]
                    sizes.append(max(map(lambda item : len(item), client_ips)) + 2)
                    sizes.append(max(map(lambda item : len(str(item)), client_ports)) + 2)
                    sizes.append(max(map(lambda item : len(str(item)), client_part)) + 2)

                    # print the table

                    print('+{}+{}+{}+{}+'.format('-'*sizes[0], '-'*sizes[1], '-'*sizes[2], '-'*sizes[3]))

                    print('|{0:^{4}}|{1:^{5}}|{2:^{6}}|{3:^{7}}|'.format(
                        client_ids[0], client_ips[0], client_ports[0], client_part[0],
                        sizes[0], sizes[1], sizes[2], sizes[3]
                    ))

                    print('+{}+{}+{}+{}+'.format('-'*sizes[0], '-'*sizes[1], '-'*sizes[2], '-'*sizes[3]))

                    for i in range(1, len(client_ids)):
                        print('|{0:^{4}}|{1:^{5}}|{2:^{6}}|{3:^{7}}|'.format(
                            client_ids[i], client_ips[i], client_ports[i], client_part[i],
                            sizes[0], sizes[1], sizes[2], sizes[3]
                        ))

                    print('+{}+{}+{}+{}+'.format('-'*sizes[0], '-'*sizes[1], '-'*sizes[2], '-'*sizes[3]))

                    # reliase memory
                    del(client_ids)
                    del(client_ips)
                    del(client_ports)
                    del(client_part)

                except ValueError:
                    print('[-] No clients exists yet ...')

            elif command == 'clear':
                if str(platform.system()) == 'Windows': system('cls')
                else: system('clear')

            else:
                print('[-] Command not recognized')
        
        sleep(10)
        #close the opened log files
        self.server_log.close()
        self.error_log.close()

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
        server_start = threading.Thread(target=self.__main_server_start)
        master_input = threading.Thread(target=self.__main_master_input)
        
        # start both threads
        server_start.start()
        master_input.start()

        #join both threads
        server_start.join()
        master_input.join()
        
        #double check for log file closing
        self.server_log.close()
        self.error_log.close()


# end of the server class
