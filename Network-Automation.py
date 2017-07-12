#!/usr/bin/env python
# --*coding:utf8*--
import os
import netmiko
import json
from base_tools import \
    get_username_and_password, get_command, write_to_the_file

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
    try:
        connection = netmiko.ConnectHandler(**device)
        prompt = connection.base_prompt
        print("already connecting to the", devicename)
        if not os.path.exists(prompt):
            os.mkdir(prompt)
        for command in commands:
            file_name = command.strip().replace(" ", "_")
            print("writing to the file " + file_name)
            write_to_the_file(".\%s\%s.txt" % (prompt, file_name),
                              connection.send_command(command))
    except connection_exception as e:
        print("Can not connection to device %s, for the reason %s"
              % (devicename, e))
