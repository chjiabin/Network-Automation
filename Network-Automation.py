#!/usr/bin/env python
# --*coding:utf8*--

import netmiko
import json
from tools import get_username_and_password, get_command


with open("Devices.json", encoding='utf-8') as f:
    devices = json.load(f)

connection_exception = (netmiko.NetMikoTimeoutException,
                        netmiko.NetMikoAuthenticationException)
username, password = get_username_and_password()
commands = get_command("router-command.txt")
for devicename, device in devices.items():
    device["username"] = username
    device["password"] = password
    print("~" * 79)
    try:
        connection = netmiko.ConnectHandler(**device)
        for command in commands:
            print(connection.send_command(command))
    except connection_exception as e:
        print("Can not connection to device %s, for the reason %s"
              % (devicename, e))
