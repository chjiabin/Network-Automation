#!/usr/bin/env python
# --*coding:utf8*--

import netmiko

devices_ip = """
192.168.25.101
192.168.25.102
192.168.25.103
192.168.25.104
""".strip().splitlines()

devices = {
    "R1": {"device_type": "cisco_ios",
           "username": "cisco",
           "password": "cisco",
           },
    "R2": {"device_type": "cisco_ios",
           "username": "cisco",
           "password": "cisco",
           },
    "R3": {"device_type": "cisco_ios",
           "username": "cisco",
           "password": "cisco",
           },
    "R4": {"device_type": "cisco_ios",
           "username": "cisco",
           "password": "cisco",
           }
}


connection_exception = (netmiko.NetMikoTimeoutException,
                        netmiko.NetMikoAuthenticationException)

for (devicename, device, device_ip) in zip(devices.keys(),
                                           devices.values(), devices_ip):
    device["ip"] = device_ip
    try:
        connection = netmiko.ConnectHandler(**device)
        print(connection.send_command("show clock"))
    except connection_exception as e:
        print("Can not connection to device %s, for the reason %s"
              % (devicename, e))
