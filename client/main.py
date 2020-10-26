from libs.client import Client

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