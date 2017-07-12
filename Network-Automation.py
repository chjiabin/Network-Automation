#!/usr/bin/env python
# --*coding:utf8*--
import netmiko
import json
from base_tools import \
    get_username_and_password, get_command
from network_tools import interface_tools

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


for devicename, device in devices.items():
    device["username"] = username
    device["password"] = password
    print("~" * 79)
    device_info_get = interface_tools(
        devicename=devicename, devices_info=device, commands=commands)
    device_info_get.no_shutdown_all_interface()
