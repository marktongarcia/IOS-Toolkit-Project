import re
import ipaddress
from jinja2 import Environment, FileSystemLoader


def regex():
    configline = "ip address {{Management_Subnet}}+3 255.255.255.224"
    result = re.search(r'.*(\{\{.*\}\})(-|\+)[0-9]+', configline).group(1)
    print(result)

# jinja for expressions is used to iterate over a data collection in a template.
def jinja():
    from jinja2 import Environment, FileSystemLoader

    data = [
        {'name': 'Andrej', 'age': 34, 'ip': ipaddress.ip_address('192.168.1.1') + 1},
        {'name': 'Mark', 'age': 17, 'ip': '192.168.2.2'},
        {'name': 'Thomas', 'age': 44, 'ip': '192.168.3.3'},
        {'name': 'Lucy', 'age': 14, 'ip': '192.168.4.4'},
        {'name': 'Robert', 'age': 23, 'ip': '192.168.5.5'},
        {'name': 'Dragomir', 'age': 54, 'ip': '192.168.6.6'}
    ]

# append new key:value pair in an existing dict.
    print(data)
    for i in data:
        i['newkey'] = 'newvalue'
    print(data)

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    template = env.get_template('persons.txt')

    output = template.render(persons=data)
    print(output)


if __name__ == '__main__':
    jinja()