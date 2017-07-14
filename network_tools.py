import os
import netmiko
import re

from collections import defaultdict
from base_tools import write_to_the_file

connection_exception = (netmiko.NetMikoTimeoutException,
                        netmiko.NetMikoAuthenticationException)


class BaseConnection(object):
    """
    This is base class using by other network tools.
    the purpose of this base class is to provide the Netmiko connection handler
    and can get info from device , and provide a way to write the info to files.
    """

    def __init__(self, device_name, devices_info, commands):
        super(BaseConnection, self).__init__()
        self.device_name, self.device, self.commands = \
            device_name, devices_info, commands
        try:
            self.connection = netmiko.ConnectHandler(**self.device)
            self.prompt = self.connection.base_prompt
            print("already connecting to the", self.prompt)
        except connection_exception as e:
            print("Can not connection to device %s, for the reason %s"
                  % (self.device_name, e))

    def get_info(self, exec_commands=[]):
        # to decide  what commands will be using
        if not exec_commands:
            commands = self.commands
        else:
            commands = exec_commands
        if not isinstance(exec_commands, list):
            print("The command must put into a list!!")
            return False
        # execute the commands
        for command in commands:
            return self.connection.send_command(command)

    def get_info_and_write_into_separate_file(self, exec_commands=[]):
            if not os.path.exists(self.prompt):
                os.mkdir(self.prompt)
            for commands in exec_commands:
                commands_output = self.get_info([commands])
                file_name = str(commands).replace(" ", "_")
                print("writing to the file " + file_name)
                if commands_output:
                    write_to_the_file(".\%s\%s.txt" % (self.prompt, file_name), commands_output)


class InterfaceTools(BaseConnection):
    """
    This module providing some functions that involved with interfaces 
    like shutdown all interface
    undo shutdown all interface
    shutdown interface that is no in using 
    make description for interface by checking the cdp neighbor.
    """

    def __init__(self, device_name, devices_info, commands):
        super(InterfaceTools, self).__init__(
            device_name, devices_info, commands)

    def get_all_interface(self):
        interfaces = []
        for line in self.get_info(["show ip int b"]).splitlines()[1:]:
            interfaces.append(re.split(r"\s+", line)[0])
        return interfaces

    def no_shutdown_all_interface(self):
        for interface in self.get_all_interface():
            commands = ["interface %s \n" % interface, "no shutdown"]
            print(self.connection.send_config_set(commands))

    def get_cdp_neighbors_information(self):
        neighbor_information = defaultdict(list)
        for neighbor_entry in (neighbor_entrys.split()
                               for neighbor_entrys in self.get_info(["show cdp neighbor"]).splitlines()[5:]):
            neighbor_information[neighbor_entry[1] + neighbor_entry[2]].append(neighbor_entry[0]+"-"+neighbor_entry[-2]+neighbor_entry[-1])
        return neighbor_information

    def make_neighbor_description(self):
        neighbor_information = self.get_cdp_neighbors_information()
        description_commands = []
        for interface, neighbors in neighbor_information.items():
            interface_command = "interface " +interface
            neighbor_command = "description Connect_to-"
            for neighbor in neighbors:
                neighbor_command += "-"+neighbor
            description_commands += [interface_command, neighbor_command, "exit"]
        return self.connection.send_config_set(description_commands)


