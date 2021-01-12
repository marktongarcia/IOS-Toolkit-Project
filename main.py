#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK


# Automating multiple firewalls
import marklib as x  # marklib.py should be in the same directory with this script (or in sys.path)
import threading  # used in function threader.
import argparse
import sys
import argcomplete
from scp import SCPClient
import click
import requests, json
import ssl

__author__ = "Mark Garcia"
__copyright__ = "Copyright 2020"
__version__ = 1.01
__maintainer__ = "Mark Garcia"
__email__ = "garcia.markanthony@gmail.com"
__status__ = "Development"


# pycharm is using a modified console which is incompatible with getpass module.
# Use terminal instead to run script or use raw for testing.
# password = getpass.getpass('Password: ')
# password = getpass._raw_input('Password: ')


def tcpcheck(ip, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()


def listping(obj, hostname, file, switch, verbose):
    hostnames = list()
    if hostname is None and file is None:
        print('No hostname provided, use the -f option')
        exit(1)
    elif hostname is None and file is not None:
        try:
            with open(file, 'r') as inputfile:
                hostnames = inputfile.read().splitlines()
        except FileNotFoundError:
            print("Unable to open file:", file)
            exit(1)
    else:
        hostnames.append(hostname)
    red = fg(1)
    green = fg(2)
    res = attr('reset')
    for site in hostnames:
        print(
            (green + site + ' is reachable' + res) if tcpcheck(site, 22, 3) else (red + site + ' is unreachable' + res))
        if switch:
            print(((green + site + '-SW is reachable' + res) if tcpcheck(site + '-SW', 22, 3) else (
                    red + site + '-SW is unreachable' + res)))


def backup(router):
    try:
        # client = x.connect(**router)  # **kwargs for dict argument
        client = x.connect(router)  # **kwargs or **routers for dict argument
        shell = x.get_shell(client)

        x.send_command(shell, 'terminal length 0', timeout=1)
        x.send_command(shell, 'enable', timeout=1)
        x.send_command(shell, 'cisco', timeout=1)  # this is the enable password
        x.send_command(shell, 'show run')

        output = x.show(shell)

        # processing the output
        # print(output)
        output_list = output.splitlines()
        output_list = output_list[15:-1]
        # print(output_list)
        output = '\n'.join(output_list)
        # print(output)

        # creating the backup filename
        from datetime import datetime
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        # if passed argument is dict
        # file_name = f'{router["server_ip"]}_{year}-{month}-{day}.txt'
        file_name = f'{router}_{year}-{month}-{day}.txt'
        print(file_name)

        # writing the backup to the file with dated filename
        with open(file_name, 'w') as f:
            f.write(output)

        # write another backup to file with just the hostname for git
        # if passed argument is dict x.connect(**routers)
        # with open(f'{router["server_ip"]}.txt', 'w') as f:
        with open(f'{router}.txt', 'w') as f:
            f.write(output)

        # closing the ssh session if active
        x.close(client)
    except TimeoutError as e:
        print(f'{router} is unreachable [TimeoutError]: {e}')
    finally:
        pass


# api using cookie or token using Authentication
def apix():
    authdata = {'username': 'admin', 'password': 'admin'}
    url = "http://192.168.1.13:8000/login/?next=/"
    r = requests.post('http://192.168.1.13:8000/login/?next=/', data=json.dumps(authdata), verify=False, proxies=None)
    print(r)
    token = json.loads(r.text)['session']
    print(token)


# api using pre-defined token access
def apiy():
    # test info
    testip = "192.168.1.201"
    # api query
    url = "http://192.168.1.13:8000/api/ipam/ip-addresses/?q=" + testip
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': 'Token 0123456789abcdef0123456789abcdef01234567'}
    r = requests.get(url, headers=headers, verify=False, proxies=None)
    # j = (r.json())
    j = json.loads(r.text)
    # view output in nice json.  not required when returning the result to be used outside this function.
    # print(json.dumps(j['results'], indent=4))

    # get id and return to be used to query for other ip of this id.
    # print(j['results'][0]['id'])
    return j['results'][0]['id']


def threader(function, routers):
    try:
        # creating an empty list (it will store the threads)
        threads = list()  # list (list() / []) can also store any objects including abstract objects like threads.
        for router in routers:
            # creating a thread for each router in the list, that executes the backup function
            th = threading.Thread(target=backup, args=(router,))  # constructor that creates a thread.  'router'
            # is a tuple and when you  want a tuple with only one element, you should add a comma after that single element.
            threads.append(th)  # appending the thread to the list
        # starting the threads
        for th in threads:  # this will start each threads.
            th.start()
        # waiting for the threads to finish
        for th in threads:
            th.join()  # this will wait for the threads to finish executing.
    except TimeoutError as e:
        print(f'{router} is unreachable [TimeoutError]: {e}')
    finally:
        pass


# def main(function, *routers)
def main():
    # print(f'function is {function} and list arg is {routers}')
    # exit(1)
    # threader(function, *routers)

    # instantiate parser object
    parser = argparse.ArgumentParser(
        description='cisco ios toolkit',
        usage='iostoolkit.py [command] [-options]',
        epilog='Example:\n"python3 iostoolkit.py backup -f ./hostlist.txt -t"',
        allow_abbrev=True,
        add_help=True)

    # main options / optional arguments
    parser.add_argument("-s", "--show", help="shows arguments", action="store_true")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')

    # create subparser - problem with this is that it does not store a arg for up or down. also because it is not an
    # option, it becomes selected after defining devices which accepts 1 or more args nargs="+". fix by changing to 1.
    # added dest so we can store subaprser selection as attribute/argument to be used in conditionals.
    subparsers = parser.add_subparsers(help="", title="Commands", dest="command", metavar="")

    # upload
    upload_parser = subparsers.add_parser("upload", help="upload a file",
                                          usage="iostoolkit.py upload [file] [remote path] [device list] [-options]")
    upload_parser.add_argument("scpfile", help="upload local file Default=ssh user home dir")
    upload_parser.add_argument("path", action="store", help="remote path | Default=overwrite existing file")
    upload_parser.add_argument("-s", "--show", help="shows arguments and device list", action="store_true")
    # define mutually exclusive group for optional args. only one option from the group can be used.
    device = upload_parser.add_mutually_exclusive_group(required=True)
    device.add_argument("-d", "--device", nargs="+", metavar='', help="hostname or ip delimited by space")
    device.add_argument("-f", "--file", help="file with the list of hostnames", type=str)

    # download
    download_parser = subparsers.add_parser("download", help="download a file",
                                            usage="iostoolkit.py download [file] [local path] [device list] [-options]")
    download_parser.add_argument("scpfile", action="store", help="download remote file")
    download_parser.add_argument("path", action="store", help="local path | Default=script dir")
    download_parser.add_argument("-s", "--show", help="shows arguments and device list", action="store_true")
    device = download_parser.add_mutually_exclusive_group(required=True)
    device.add_argument("-d", "--device", nargs="+", metavar='', help="hostname or ip delimited by space")
    device.add_argument("-f", "--file", help="file with the list of hostnames", type=str)

    # backup
    backup_parser = subparsers.add_parser("backup", help="backup running-config in local dir",
                                          usage="iostoolkit.py backup [device list] [-options]")
    backup_parser.add_argument("-s", "--show", help="shows arguments and device list", action="store_true")
    backup_parser.add_argument('-t', '--threading', help='enable threading', action='store_true', default=False)
    device = backup_parser.add_mutually_exclusive_group(required=True)
    device.add_argument("-d", "--device", nargs="+", metavar='', help="hostname or ip delimited by space")
    device.add_argument("-f", "--file", help="file with the list of hostnames", type=str)

    # api
    api_parser = subparsers.add_parser("api", help="backup running-config in local dir",
                                       usage="iostoolkit.py backup [device list] [-options]")
    api_parser.add_argument("username", action="store")
    api_parser.add_argument("password", )
    api_parser_g = api_parser.add_mutually_exclusive_group()
    api_parser_g.add_argument("--display", help="display authentication", action="store_true")
    api_parser_g.add_argument("--get")
    api_parser.add_argument("-s", "--show", help="shows arguments and device list", action="store_true")
    api_parser.add_argument('-t', '--threading', help='enable threading', action='store_true', default=False)
    device = api_parser.add_mutually_exclusive_group(required=True)
    device.add_argument("-d", "--device", nargs="+", metavar='', help="hostname or ip delimited by space")
    device.add_argument("-f", "--file", help="file with the list of hostnames", type=str)

    # alternative, pass a single required arg based only on choices provided ans store as function.  print(args.function)
    # parser.add_argument(dest="scp", nargs="?", choices=["tea", "download"], help="select function to use")

    # tab autocomplete using argcomple package. ## TESTING, not yet working
    argcomplete.autocomplete(parser)

    # parse the cli options and show help if only 1 argument is defined ie: 'toolkit.py'.
    # print(sys.argv)
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    # process arguments
    #    try:
    #        print(parser.parse_args())
    #    except IOError as msg:
    #        parser.error(str(msg))
    try:
        # show args
        if args.show and args.command is None:
            print(parser.parse_args())
        elif args.device and args.show:
            print(parser.parse_args())
            # print(f'your args are {args}')
        elif args.file and args.show:
            print(parser.parse_args())
            print("below are the file contents:")
            with open(args.file, 'r') as inputfile:
                routers = inputfile.read().splitlines()
                for router in routers:
                    print(router)
        # backup device
        elif args.command == "backup" and args.device and args.threading is False:
            for dev in args.device:
                # print(dev)
                # exit(1)
                backup(dev)
        elif args.command == "backup" and args.device and args.threading:
            threader(backup, args.device)
            ## for dev in args.device:
            # print(dev)
            # exit(1)
            ## threading(backup, dev)
        # backup from file list
        elif args.command == "backup" and args.file and args.threading is False:
            # print(args.file)
            # exit(1)
            # parse file using input as list of str.
            try:
                with open(args.file, 'r') as inputfile:
                    inputfile = inputfile.read().splitlines()
                    # remove accidental blank in the list, these blanks returns all records in database.
                    routers = list(filter(None, inputfile))
                    for router in routers:
                        backup(router)
            except FileNotFoundError as e:
                print(f'There is an error FileNotFoundError: {e}')
            finally:
                pass
        elif args.command == "backup" and args.file and args.threading:
            # print(args.file)
            try:
                with open(args.file, 'r') as inputfile:
                    inputfile = inputfile.read().splitlines()
                    # remove accidental blank in the list, these blanks returns all records in database.
                    routers = list(filter(None, inputfile))
                    threader(backup, routers)
            except FileNotFoundError as e:
                print(f'There is an error FileNotFoundError: {e}')
            finally:
                pass
        # scp upload/put and download/get
        elif args.command == "upload" or args.command == "download" and args.device is not None:
            # print(locals())
            # # print(globals())
            if click.confirm(f'local file: {args.scpfile}\nremote path: {args.path}\n\n Do you want to proceed?',
                             default=False):
                for dev in args.device:
                    x.scp_connect(dev, args.scpfile, args.path, args.command)
        # scp to/from a list of devices from file
        elif args.command == "upload" or args.command == "download" and args.file is not None:
            if click.confirm(f'local file: {args.scpfile}\nremote path: {args.path}\n\n Do you want to proceed?',
                             default=False):
                try:
                    with open(args.file, 'r') as inputfile:
                        inputfile = inputfile.read().splitlines()
                        # remove accidental blank in the list, these blanks returns all records in database.
                        routers = list(filter(None, inputfile))
                        for router in routers:
                            x.scp_connect(router, args.scpfile, args.path, args.command)
                except FileNotFoundError as e:
                    print(f'There is an error FileNotFoundError: {e}')
                except TimeoutError as e:
                    print(f'{router} is unreachable [TimeoutError]: {e}')
                finally:
                    pass
                for dev in args.device:
                    x.scp_connect(dev, args.scpfile, args.path, args.command)
        # apiy
        elif args.comman == "api":
            apiy()
        else:
            print("Error:Requires an argument to perform an action")
    # exceptions for error handling
    except AttributeError as e:
        print(f'there is an AttributeError: {e}')
    except UnicodeError as e:
        print(f'there is an UnicodeError: {e}')


#     if threading == 1:
#         threader(function)
#     else:
#         function(routers)
# pass
#    if function is None and routers is None:
#     routers = list()
#     if routers is None and file is None:
#         print('No hostname provided, use the -h option')
#         exit(1)
#     elif routers is None and file is not None:
#         try:
#             with open(file, 'r') as inputfile:
#                 routers = inputfile.read().splitlines()
#             print(routers)
#         except FileNotFoundError:
#             print("Unable to open file:", file)
#             exit(1)

# main.add_command(backup)

if __name__ == '__main__':
    # apiy()
    main()