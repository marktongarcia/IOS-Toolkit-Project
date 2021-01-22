import paramiko
import time
from scp import SCPClient


class Remote(object):
    """
    Container class for SSH functionality. Needs to be used in a with statement.
    basically a paramiko class for use in a "with" block that automatically opens and closes a session.
    """

    def __init__(self, hostname, username, password, verbose=False):
        self.host = hostname
        self.user = username
        self.password = password
        self.verbose = verbose
        # if 'paramiko' in sys.modules.key():
        #     self._has_paramiko = True
        # else:
        #     print('Please import paramiko module')
        #     self._has_paramiko = False

    def __enter__(self):
        # if not self._has_paramiko():
        #     raise ModuleNotFoundError('Please import paramiko')
        # else:
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # to avoid
        # paramiko.ssh_exception.SSHException: Server '192.168.1.201' not found in known_hosts
        print(f'\nConnecting to {self.host}...')
        self.ssh_client.connect(hostname=self.host, username=self.user, password=self.password)
        self.shellchannel = self.ssh_client.invoke_shell()  # this is opening a channel where you send and recv.
        print('Successfully connected')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.ssh_client is not None:
                print('Closing connection...\n')
                self.ssh_client.close()
        except:
            print("received an exception closing the ssh connection.")
        finally:
            self.ssh_client = None

    def execute(self, command, sudo=False):
        # if not self._has_paramiko():
        #     print('self has no paramiko')
        #     return None, None, None

        stdin, stdout, stderr = self.execute(command)
        exit(1)
        if sudo:
            stdin.write(self.password + '\n')
            stdin.flush()

        return stdin, stdout, stderr

    # def get_shell(self):
    #     # get shell
    #     shellchannel = self.ssh_client.invoke_shell()
    #     print('Successfully connected')
    #     self.shell = shellchannel
    #     return self

    def shell(self, command, timeout=1):
        if self.verbose:
            print(f'sending command line {command}')
        # send command
        # print(command)
        self.shellchannel.send(command + '\n')
        time.sleep(timeout)
        # print(shellchannel.recv(10000).decode('utf-8'))
        # return self

    def send_from_file(self, file_name):
        # print(self.shell)
        # exit(1)
        if self.verbose:
            print(f'Opening file {file_name}')
        with open(file_name) as f:
            commands = f.read().splitlines()
            # remove accidental blank in the list.
            commands = list(filter(None, commands))
            print('Configuring device...')
            if self.verbose:
                print(f'sending commands to {self.user}: {commands}')
            for cmd in commands:
                # print(cmd)
                self.shell(cmd)

    # SCP upload or download
    def scp_connect(self, file, path, command=None, timeout=1):
        # create scp object.  same name as the module is ok because this is not a function but an object.
        scp = SCPClient(self.ssh_client.get_transport())
        if command == "upload":
            # put / upload file
            print(f'\nCopying file "{file}" to "{self.host}" in directory "{path}"...')
            scp.put(file, path)
            time.sleep(timeout)
        elif command == "download":
            # get / download
            print(f'\ndownloading file "{file}" to local directory "{path}"...')
            scp.get(file, path)
            time.sleep(timeout)
        # close the connection
        print(f'\nClosing scp session to "{self.host}"...')
        scp.close()

    def show(self, n=10000):
        # print(self.shell)
        # exit(1)
        # print(self.shellchannel.recv(n).decode('utf-8'))

        return self.shellchannel.recv(n).decode('utf-8')
        # output = self.shell.recv(n)
        # return output.decode('utf-8')
        # print(output.decode())

    # def _has_paramiko(self):
    #     return 'paramiko' in sys.modules.keys()


# def get_auth():
#     print("Enter your ssh credentials")
#     self.user = raw_input("Enter user name: ")
#     self.password = getpass.getpass("Enter your password: ")
#
#
# if username is None and password is None:
#     print('tae')
#     exit(1)
#     get_auth()

if __name__ == '__main__':
    devices = ['192.168.1.201', '192.168.1.202']
    for dev in devices:
        with Remote(hostname=dev, username='cisco', password='cisco', verbose=True) as x:
            '''
            # with Remote(hostname='192.168.1.12', username='gns3', password='gns3', verbose=True) as x:
            print(x.__init__)
            exit(1)
            # sample shell()
            x.shell('terminal length 0\n')
            '''
            # sample sendcmd()
            x.send_from_file('./commands.txt', verbose=False)
            if x.verbose:
                output = x.show()
                print(output)
            '''
            # sample scp_connect()
            x.scp_connect('deleteme.txt', 'tae.txt', command='download')
            '''
