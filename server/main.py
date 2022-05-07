# !/usr/bin/python

from libs.server_module import Server
from libs.colors import COLORS
from socket import gethostbyname, gethostname
from os import system
from platform import system as operatingsys
from re import findall

#define functions
def proccess_data(data):
    """
    DOCSTRING: this function will exract all the given information in the
    config file using regex. And it will return a dictionary containing
    all the main part as keys and sub infor as values
    
    data: raw string containgin file data 
    """
    # filter main parts of configuration
    results = findall(r'(\[.*\])([\w\s\.,:]*)(?=#end)', data)
    # extracted data will store in this dictionary
    configuration = {}

    # group for main configurations after deviding to sections
    for result in results:
        # check if this is host: 192.168.45.32 kind of configuration
        val_filter = findall(r'(\w+):\s(.*)', result[1])

        # if so it will be add to main configuration dictionary
        # value as a dictionary sub configurations as the key
        if val_filter:
            configuration[result[0][1:-1]] = {}
            for value in val_filter:
                configuration[result[0][1:-1]][value[0]] = value[1]

        # otherwise it will be added to the main configurations as a list
        else: 
            val_filter = findall(r'(\w+)', result[1])
            configuration[result[0][1:-1]] = val_filter
    
    return configuration

def read_write(data=None, read=True, defaulet_file = 'config.conf'):
    """
    DOCSTRING: this function is used to read from a file or write
    data to the file

    data: this is the data which must write to the file

    read : wheather read or write

    default_file: default name of the file
    """
    # if read the proccess is simple only wee need to read from the file
    # and give to proccess data functions to extrac data
    if read:
        with open(defaulet_file, 'r') as config_file:
            data = config_file.read()
        return proccess_data(data)

    # other wise we must create a string for the format of the config file
    # and write it to the configuration file
    if not read:
        with open(defaulet_file, 'w') as config_file:
            for key in data:
                # write main conficrations in [] brackets
                config_file.write('[{}]\n'.format(key))
                # if dict write data as port: 8080 format
                if type(data[key]) == dict:
                    for key_, value_ in data[key].items():
                        config_file.write('{}: {}\n'.format(key_, value_))
                
                # otherwise just join with commas
                else:
                    config_file.write('{}\n'.format(', '.join(data[key])))
                
                # add #end tag for the configuration files
                config_file.write('#end\n\n')

def run_commands(command):
    """
    DOCSTRING: this function will run all the given necessary commands in the terminal
    command: this is the raw string command given by the user
    """
    # wee need to change the global configuration variable to get permission
    global configuration
    # split the command in spaces
    command = command.split()

    # the start command will start the server
    if(command[0] == 'start') or (command[0] == 'run'):
        # pass the host, port ,blacklist and whitelist t the server
        host = configuration['SERVER']['host']
        port = int(configuration['SERVER']['port'])
        server = Server(host, port, configuration['BLACKLIST'])
        server.start_server()

    # the command show will print out the data in cnfiguration file
    # SYNTAX: show <configuration>
    elif command[0] == 'show':
        # in this case a key error may be occure when wron key given
        try:
            current_data = configuration[command[1].upper()]
            if type(current_data) == dict:
                for key, value in current_data.items(): print('{:<10} --> {}'.format(key, value))
            else:
                for value in current_data: print(value)

        except KeyError:
            if command[1] == 'configs':
                print('\n'.join(configuration.keys()))
            else:
                print('[-] The configuration {} not found!'.format(command[1]))

    # the set command is used to edit values in confiuratins
    # SYNTAX: set <configuration> <key> <value>
    elif command[0] == 'set':
        try:
            # command[1] is the main key of the dictinary
            # command[2] is the sub key of the dictionary / key of the value dict
            # command[3] is the new value to assigned
            configuration[command[1].upper()][command[2]] = str(command[3])
            read_write(read=False, data=configuration)

        except IndexError:
            print('[-] This command requires three arguments')
            print('SYNATX: set <configuration> <key> <value>')

        except TypeError:
            print('[-] set command is not valid for this configuration!')
            print('Try add/remove command for your purpose')

        except KeyError:
            print('[-] Configuration not found !')
            print('Try \"show configs\" to see available configurations')

    # the command quit will shut down main server handler
    elif command[0] == 'quit':
        return False

    # the command clear will clear the screen
    elif command[0] == 'clear':
        # check for the operatin system
        if str(operatingsys()) == 'Windows': system('cls')
        else: system('clear')

    elif command[0] == 'help':
        with open('libs\\help_main.txt', 'r') as help_file:
            print(help_file.read(), end='\n\n\n')

    else:
        try:
            if command[1] == 'add':
                # SYNTAX: <keyname> add <value>
                # command[2] is the value
                # command[0] is the main key
                configuration[command[0].upper()].append(command[2])
                read_write(read=False, data=configuration)
                print('{} --> {}'.format(command[2], command[0]))

            elif command[1] == 'remove':
                # SYNTAX: <keyname> remove <value>
                # command[2] is the value
                # command[0] is the main key
                try:
                    configuration[command[0].upper()].remove(command[2])
                    read_write(read=False, data=configuration)
                    print('{} --x {}'.format(command[2], command[0]))

                except ValueError:
                    print('[-] Client {} is not in {}'.format(command[2], command[0]))

            else:
                print('[-] The command is not recognized')

        except KeyError:
            print('[-] Command {} is not recognized'.format(command[0]))
        except IndexError:
            print('[-] Command {} is not recognized'.format(command[0]))

# fisrt of all clear the screen
if operatingsys() == 'Windows': system('cls')
else: system('clear')

# then print welcome message
print('ServerClient Server Version 1.0.0.0')
print('-----------------------------------\n')

# read configuration data from the config file
configuration = read_write()

while True:
    # a keyboard interubt may be occured
    try:
        # geth inputs from the user
        if run_commands(input("#SERVER/> ")) == False: break
        print() # prints a blank new line

    except KeyboardInterrupt:
        break
