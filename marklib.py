import paramiko
import time
import getpass


# pycharm is using a modified console which is incompatible with getpass module.
# Use terminal instead to run script or use raw for testing.
# password = getpass.getpass('Password: ')
# password = getpass._raw_input('Password: ')


def connect(server_ip):
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'\nConnecting to {server_ip}...')
    ssh_client.connect(hostname=server_ip, port=22, username='cisco', password='cisco',
                       look_for_keys=False, allow_agent=False)
    # Below is if your passing a dictionary.  "def connect(server_ip, server_port, user, passwd):"
    # ssh_client.connect(hostname=server_ip, port=server_port, username=user, password=passwd, look_for_keys=False,
    # allow_agent=False) if you want to use a local variable outside the function in which it is defined; you have to
    # "return" it.
    return ssh_client


# connect to a list of dict.  used sample in local __main__.
def xconnect(server_ip, server_port, user, passwd):
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'\nConnecting to {server_ip}...')
    # Below is if your passing a dictionary.  "def connect(server_ip, server_port, user, passwd):"
    ssh_client.connect(hostname=server_ip, port=server_port, username=user, password=passwd,
                       look_for_keys=False, allow_agent=False)
    # if you want to use a local variable outside the function in which it is defined; you have to "return" it.
    return ssh_client


def get_shell(ssh_client):
    shellchannel = ssh_client.invoke_shell()  # read about invoke_shell vs exec_command
    print('Successfully connected')
    return shellchannel


def send_command(shell, command, timeout=1):
    # print(f'Sending command: {command}')
    shell.send(command + '\n')
    time.sleep(timeout)


def send_from_file(shell, file_name, time=5):
    print(f'Opening file {file_name}')
    with open(file_name) as f:
        commands = f.read().splitlines()
        # remove accidental blank in the list.
        commands = list(filter(None, commands))
        print(f'sending commands to {shell}: {commands}')
        for cmd in commands:
            send_command(shell, cmd.lower())


def show(shell, n=10000):
    xoutput = shell.recv(n)  # reading shell output buffer in bytes.
    # decoding from bytes to string.  'utf-8' is the default value so you can leave the decode function empty as well.
    return xoutput.decode('utf-8')


def close(ssh_client):  # close the ssh session if active.
    if ssh_client.get_transport().is_active():
        print('Closing connection...\n')
        ssh_client.close()


# SCP upload or download
def scp_connect(server_ip, file, path, command=None, timeout=1):
    from scp import SCPClient

    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'\nConnecting to {server_ip}...')
    ssh_client.connect(hostname=server_ip, port=22, username="gns3", password="gns3", look_for_keys=False,
                       allow_agent=False)
    # create scp object.  same name as the module is ok because this is not a function but an object.
    scp = SCPClient(ssh_client.get_transport())
    if command == "upload":
        # put / upload file
        print(f'\nCopying file "{file}" to "{server_ip}" in directory "{path}"...')
        scp.put(file, path)
        time.sleep(timeout)
    elif command == "download":
        # get / download
        print(f'\ndownloading file "{file}" to local directory "{path}"...')
        scp.get(file, path)
        time.sleep(timeout)
    # close the connection
    print(f'\nClosing scp session to "{server_ip}"...')
    scp.close()


# def scp_(server_ip, file, rpath, timeout=1):
#     from scp import SCPClient
#
#     ssh_client = paramiko.SSHClient()
#     ssh_client.load_system_host_keys()
#     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     print(f'\nConnecting to {server_ip}...')
#     ssh_client.connect(hostname=server_ip, port=22, username="gns3", password="gns3", look_for_keys=False,
#                        allow_agent=False)
#     # create scp object.  same name as the module is ok because this is not a function but an object.
#     scp = SCPClient(ssh_client.get_transport())
#     # get / download file
#     print(f'\nCopying file "{file}" to "{server_ip}" in directory "{rpath}"...')
#     scp.get(file, lpath)
#     time.sleep(timeout)
#     # close the connection
#     print(f'\nClosing scp session to "{server_ip}"...')
#     scp.close()


# this will make sure that anything below will only run when directly running the
# module itself but not when importing it to a another python file / script.
if __name__ == '__main__':
    # creating a dictionary for each device to connect to
    router1 = {'server_ip': '192.168.1.201', 'server_port': '22', 'user': 'cisco', 'passwd': 'cisco'}
    router2 = {'server_ip': '192.168.1.202', 'server_port': '22', 'user': 'cisco', 'passwd': 'cisco'}
    router3 = {'server_ip': '192.168.1.203', 'server_port': '22', 'user': 'cisco', 'passwd': 'cisco'}

    # creating a list of dictionaries (of devices)
    routers = [router1, router2, router3]  # this list of dict needs to be the same keys as the function connect()
    for router in routers:
        client = xconnect(**router)
        # print(router)
        # exit(1)
        shell = get_shell(client)

        send_command(shell, 'enable')
        send_command(shell, 'cisco')  # this is the enable password
        send_command(shell, 'term len 0')
        send_command(shell, 'sh version')
        send_command(shell, 'sh ip int brief')

        output = show(shell)
        print(output)
