#!/usr/bin/env python
# --*coding:utf8*--

import netmiko
import json

from tools import get_username_and_password


with open("Devices.json", encoding='utf-8') as f:
    devices = json.load(f)

connection_exception = (netmiko.NetMikoTimeoutException,
                        netmiko.NetMikoAuthenticationException)

username, password = get_username_and_password()
for devicename, device in devices.items():
    device["username"] = username
    device["passwoed"] = password
    print("~" * 79)
    try:IDLE
        connection = netmiko.ConnectHandler(**device)
        print(connection.send_command("show clock"))
    except connection_exception as e:
        print("Can not connection to device %s, for the reason %s"
              % (devicename, e))
