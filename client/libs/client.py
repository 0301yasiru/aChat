# !/usr/bin/python
import socket
import threading
from libs.colors import COLORS
from platform import system

from os import remove
from sys import argv
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC



class Client():
    def __init__(self, client_id, server, port):
        """
        DOCSTRING: this function will initalize all the global varables for the class
        client_id: this is the user name of the server
        server   : this is the IP address of the server to be connecter
        port     : this is the PORT of the server to be connected
        """
        self.passwd = 'A4nJ!dk@12en#jfdk*kjns.sdjk'
        self.key = self.key_gen(self.passwd)
        self.buffer = 64
        self.client_id = client_id
        self.server = server
        self.port = port
        self.addr = (self.server, self.port)

        # create the socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5)
        # terminate varibale is the most important variable in the class
        # of the terminate varible set to True all loops will terminate imidiatly
        # all the threads will terminate
        # and the client will shutdown
        self.terminate = False

        self.c = COLORS()

    def key_gen(self, passwd):
        # convert passwd to bytes
        passwd = passwd.encode('utf-8')
        # create a random salt from os
        salt = b'\xd1\xafy\x8d\xd1/\xa1Pv4\xea\xf1-1\xe0~\xb2$\x17D\xdd\xa7\x8fwrmd\x02\x7f`f:'
        # create kdf instance
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        # derive an key prom the passwd
        key = urlsafe_b64encode(kdf.derive(passwd))
        #return key
        return key

    def decrypt(self, message):
        """
        DOCSTRING: This function will return the decrypted message as string
        message: the message to decrypt as string
        key: key for decryption as bytes
        """
        fernet_obj = Fernet(self.key) # create fernet obj
        original_content = fernet_obj.decrypt(message.encode('utf-8'))

        return original_content.decode('utf-8')

    def encrypt(self, message):
        """
        DOCSTRING: This function will return the encrypted message as string
        message: the message to encrypt as string
        key: key for encryption as bytes
        """
        fernet_obj = Fernet(self.key)
        encrypted_message = fernet_obj.encrypt(message.encode('utf-8'))

        return encrypted_message.decode('utf-8')

    def __hidden_send(self):
        """
        DOCSTRING: this is the function which uses by the thread to forward
        messages
        conn: connection of the client
        client_id: user name of the client
        """
        # while the terminate variable is False run the infinite loop
        while not self.terminate:
            # in this case a OS error will be raised when the input timeout
            try:
                current_msg = input().strip()
                if current_msg == 'conn_quit()':
                    self.terminate =True

                self.send_message(current_msg)
                print()

            except EOFError:
                exit()

    def __hidden_recv(self):
        """
        DOCSTRING: this is the function which uses by the thread to recevie messages
        conn: connection of the client
        client_id: user name of the client
        """
        while not self.terminate:
            message = self.recv_message()
            if message:
                if str(system()) == 'Windows':
                    print(f'[RECIVED] {message}')
                else:
                    print(self.c.Cyan + f'[RECIVED] {message}' + self.c.RESET)

    def send_message(self, message, encrypt_= True):
        """
        DOCSTRING: this is the primary function to sent messages anyway
        conn: connection of the client
        message: the message as an string
        client_id: user name of the client
        """
        # this function may raise an error when server is shutted down
        try:
            # before anthiyng else encrypt your message
            if encrypt_: message = self.encrypt(message)
            #fisrt of all we need to send size details
            message_size = str(len(message)).encode('utf-8')
            #procces message size details
            message_size += b' ' * (self.buffer - len(message_size))
            #send message size details
            self.client.send(message_size)
            #then send the message
            self.client.send(message.encode('utf-8'))
        
        except ConnectionAbortedError:
            print('[-] The server is down program is quiting...')
            self.terminate = True

    def recv_message(self, encrypt = True):
        """
        DOCSTRING: this is the primary function to receve messages
        conn: connection of the client
        client_id: user name of the client (this info will use to eject client)
        """
        try:
            msg_size = self.client.recv(self.buffer).decode('utf-8')
            # checking if msg is none or not if not proceed
            if msg_size:
                msg_size = int(msg_size) # this is the size of up comming message
                msg = self.client.recv(msg_size).decode('utf-8') #recive and decode
                #before return decrypt the message
                if encrypt:
                    msg = self.decrypt(msg)
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
        """
        DOCSTRING: the pusrpose of this function is simple. Al this has to do
        create two thread for sending and revceving messages. and handle
        those clients
        """
        # create threads for recive messages and send messages
        reciving_thread = threading.Thread(target=self.__hidden_recv)
        sending_thread = threading.Thread(target=self.__hidden_send)

        # start threads
        reciving_thread.start()
        sending_thread.start()

        # after disconnecting kill those threads
        reciving_thread.join()
        exit()
        sending_thread.join()

    def start_client(self):
        """
            DOCSTRING: this function will start the server
            fisrt try to connect to the server. And if sccueed
            send client data and establish the connection
        """
        # print welcome message
        print("\nClient Program started version: 1.0.0.0")
        print('---------------------------------------\n')
        print('Your Client ID -> {}'.format(self.client_id))
        print('----------------------------------------\n')

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


# end of the client class