from libs.server_module import Server
from libs.colors import COLORS
from socket import gethostbyname, gethostname
from os import system
from platform import system as operatingsys
from re import findall

#define functions
def proccess_data(data):
    # filter main parts of configuration
    results = findall(r'(\[.*\])([\w\s\.,:]*)(?=#end)', data)

    configuration = {}
    for result in results:
        val_filter = findall(r'(\w+):\s(.*)', result[1])

        if val_filter:
            configuration[result[0][1:-1]] = {}
            for value in val_filter:
                configuration[result[0][1:-1]][value[0]] = value[1]

        else: 
            val_filter = findall(r'(\w+)', result[1])
            configuration[result[0][1:-1]] = val_filter
    
    return configuration

def read_write(data=None, read=True):
    defaulet_file = 'config.conf'

    if read:
        with open(defaulet_file, 'r') as config_file:
            data = config_file.read()
        return proccess_data(data)

    if not read:
        with open(defaulet_file, 'w') as config_file:
            for key in data:
                config_file.write('[{}]\n'.format(key))
                if type(data[key]) == dict:
                    for key_, value_ in data[key].items():
                        config_file.write('{}: {}\n'.format(key_, value_))
                else:
                    config_file.write('{}\n'.format(', '.join(data[key])))
                
                config_file.write('#end\n\n')

def run_commands(command):
    global configuration
    command = command.split()
    if(command[0] == 'start') or (command[0] == 'run'):
        host = configuration['SERVER']['host']
        port = int(configuration['SERVER']['port'])
        server = Server(host, port, configuration['BLACKLIST'])
        server.start_server()

    elif command[0] == 'show':
        current_data = configuration[command[1].upper()]
        if type(current_data) == dict:
            for key, value in current_data.items(): print('{:<10} --> {}'.format(key, value))
        else:
            for value in current_data: print(value)

    elif command[0] == 'set':
        # command[1] is the main key of the dictinary
        # command[2] is the sub key of the dictionary / key of the value dict
        # command[3] is the new value to assigned
        configuration[command[1].upper()][command[2]] = str(command[3])
        read_write(read=False, data=configuration)

    elif command[0] == 'quit':
        return False

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
    if run_commands(input("#SERVER/> ")) == False: break
    print() # prints a blank new line