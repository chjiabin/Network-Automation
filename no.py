import time
import threading
from base_tools import get_username_and_password, get_command, load_info_from_json, print_the_splitlines
from network_tools import InterfaceTools, BaseConnection
from multiprocessing import Pool, Process, Queue

# Get the username and the password
# Get the command from a file, and exclued the enpty lines
# Get the devices information from a json file.
username, password = get_username_and_password()
commands = get_command("router-command.txt")
devices = load_info_from_json("Devices.json")
devices_connection_information = load_info_from_json("Connection Information.json")

'''
def get_base_hander(device):
    return BaseConnection(devices_info=device, commands=commands)

device_cxn = []
for device in devices.values():
    device_cxn.append(get_base_hander(device))

for _ in device_cxn:
    _.config(["interface fa 0/0", "shutdown"])
'''

from multiprocessing import Process
import os


# 子进程要执行的代码
def run_proc(name):
    print('Run child process %s (%s)...' % (name, os.getpid()))

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_proc, args=('test',))
    print('Child process will start.')
    p.start()
    p.join()
    print('Child process end.')