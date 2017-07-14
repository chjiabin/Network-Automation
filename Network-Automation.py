#!/usr/bin/env python
# --*coding:utf8*--
import netmiko
import json
from base_tools import get_username_and_password, get_command
from network_tools import BaseConnection, InterfaceTools

# Read the devices information from a file, should be written in JSON
with open("Devices.json", encoding='utf-8') as f:
    devices = json.load(f)
# Some exception need to be handled
connection_exception = (netmiko.NetMikoTimeoutException,
                        netmiko.NetMikoAuthenticationException)
# Get the username and the password
username, password = get_username_and_password()
# Get the command from a file, and exclued the enpty lines
commands = get_command("router-command.txt")


for device_name, device in devices.items():
    device["username"] = username
    device["password"] = password
    print("~" * 79)
    device_info_get = InterfaceTools(
        device_name=device_name, devices_info=device, commands=commands)
    print(device_info_get.shutdown_unused_interface())
