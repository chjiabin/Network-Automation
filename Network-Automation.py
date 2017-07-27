#!/usr/bin/env python
# --*coding:utf8*--
import time
from base_tools import get_username_and_password, get_command, load_devices_info_from_json
from network_tools import BaseConnection, InterfaceTools


# print the prompt before each session, by using decorate function.
def print_the_splitlines(fun):
    def inner(*args, **kw):
        print("~" * 79)
        device["username"] = username
        device["password"] = password
        fun(*args, **kw)
    return inner


@print_the_splitlines
def action(device):
    device_action = InterfaceTools(devices_info=device, commands=commands)
    device_action.no_shutdown_all_interface()
    device_action.make_neighbor_description()
    # device_action.shutdown_unused_interface()

start = time.time()
# Get the username and the password
# Get the command from a file, and exclued the enpty lines
# Get the devices information from a json file.
username, password = get_username_and_password()
commands = get_command("router-command.txt")
devices = load_devices_info_from_json("Devices.json")

if __name__ == '__main__':
    for device in devices.values():
        action(device)
    end = time.time()
    print("the time spend on cal is:", end-start)
