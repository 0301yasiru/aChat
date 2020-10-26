with open('client.conf', 'w') as conf_file:
    data = []
    uname = input('Enter User Name -> ')
    conf_file.write(f'client_id: {uname}\n')
    host = input('Enter Server Address -> ')
    conf_file.write(f'host: {host}\n')
    port = input('Enter Port Number -> ')
    conf_file.write(f'port: {port}\n')