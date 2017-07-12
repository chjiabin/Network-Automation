import os
import netmiko
import re
from base_tools import write_to_the_file

connection_exception = (netmiko.NetMikoTimeoutException,
                        netmiko.NetMikoAuthenticationException)


class base_connection(object):
    """docstring for information_get"""

    def __init__(self, devicename, devices_info, commands):
        super(base_connection, self).__init__()
        self.devicename, self.device, self.commands = \
            devicename, devices_info, commands
        try:
            self.connection = netmiko.ConnectHandler(**self.device)
            self.prompt = self.connection.base_prompt
            print("already connecting to the", self.prompt)
        except connection_exception as e:
            print("Can not connection to device %s, for the reason %s"
                  % (self.devicename, e))

    def get_info(self, exec_commands=""):
        # decise what commands will be using
        if not exec_commands:
            commands = self.commands
        else:
            commands = exec_commands
        # execute the commands
        for command in commands.splitlines():
            return self.connection.send_command(command)

    def get_info_and_write_into_seperete_file(self, exec_commands=""):
        # decise what commands will be using
        if not exec_commands:
            commands = self.commands
        else:
            commands = exec_commands
        # execute the commands
        for command in commands.splitlines():
            if not os.path.exists(self.prompt):
                os.mkdir(self.prompt)
            file_name = command.strip().replace(" ", "_")
            print("writing to the file " + file_name)
            write_to_the_file(".\%s\%s.txt" % (self.prompt, file_name),
                              self.connection.send_command(command))


class interface_tools(base_connection):
    """docstring for interface_tools"""

    def __init__(self, devicename, devices_info, commands):
        super(interface_tools, self).__init__(
            devicename, devices_info, commands)

    def get_all_interface(self):
        interfaces = []
        for line in self.get_info("show ip int b").splitlines()[1:]:
            interfaces.append(re.split(r"\s+", line)[0])
        return interfaces

    def no_shutdown_all_interface(self):
        for interface in self.get_all_interface():
            commands = ["interface %s \n" % interface, "no shutdown"]
            print(self.connection.send_config_set(commands))
