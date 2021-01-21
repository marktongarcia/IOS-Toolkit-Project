


try:
    import paramiko, getpass
    import sys
    import time
except ImportError:
    pass

class Remote(object):
    """
    Container class for SSH functionality. Needs to be used in a with statement.
    basically a paramiko class for use in a "with" block that automatically opens and closes a session.
    """

    def __init__(self, hostname, username, password):
        self.host = hostname
        self.user = username
        self.password = password

    def __enter__(self):
        if self._has_paramiko():
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.load_system_host_keys()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print(f'\nConnecting to {self.host}...')
            self.ssh_client.connect(hostname=self.host, username=self.user, password=self.password)
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

    def connect(self):
        if not self._has_paramiko():
            return
        if self.user is None and self.password is None:
            self._get_auth()
        try:
            self.connect()
            exit(1)
        except paramiko.AuthenticationException:
            print("you entered an incorrect username or password.  Please try again")
            self._get_auth()
            try:
                self.ssh_client.connect(server, username=self.user, password=self.password)
            except:
                print("you entered an incorrect username or password a second time. Exiting")
                sys.exit(1)

    def execute(self, command, sudo=False):
        if not self._has_paramiko():
            print('self has no paramiko')
            return None, None, None

        stdin, stdout, stderr = self.execute(command)
        exit(1)
        if sudo:
            stdin.write(self.password + '\n')
            stdin.flush()

        return stdin, stdout, stderr

    def shell(self, command, timeout=1):
        # get shell
        shellchannel = self.ssh_client.invoke_shell()
        print('Successfully connected')
        # send command
        shellchannel.send(command + '\n')
        time.sleep(timeout)
        self.shell = shellchannel
        # return

    def show(self, n=10000):
        # print(self.shell)
        # exit(1)
        output = self.shell.recv(n)
        return output.decode('utf-8')
        print(output.decode())

    def _get_auth(self):
        print("Enter your ssh credentials")
        self.user = raw_input("Enter user name: ")
        self.password = getpass.getpass("Enter your password: ")

    def _has_paramiko(self):
        return 'paramiko' in sys.modules.keys()


with Remote(hostname='192.168.1.201', username='cisco', password='cisco') as x:
    x.shell('show version\n')
    x.shell('enable\n')
    x.shell('conf t\n')
    x.shell('int loopback 123\n')
    x.shell('ip address 123.0.0.1 255.255.255.0\n')
    x.show()
    pass