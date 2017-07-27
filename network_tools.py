import os
import re
import netmiko
from collections import defaultdict
from base_tools import write_to_the_file, dedupe

connection_exception = (netmiko.NetMikoTimeoutException,
                        netmiko.NetMikoAuthenticationException)


class BaseConnection(object):
    """
    This is base class using by other network tools.
    the purpose of this base class is to provide the Netmiko connection handler
    and can get info from device , and provide a way to write the info to files.
    """

    def __init__(self, devices_info, commands=()):
        super(BaseConnection, self).__init__()
        # Netmiko does not take device_name info, so here need to pop the device_name info.
        self.device_name, self.commands = devices_info["device_name"], commands
        # getting a new dict and filter the key "device_name"
        self.device = dict((key, value) for key, value in devices_info.items() if key != "device_name")
        try:
            self.connection = netmiko.ConnectHandler(**self.device)
            self.prompt = self.connection.base_prompt
            print("already connecting to the", self.prompt)
        except connection_exception as e:
            print("Can not connection to device %s, for the reason %s"
                  % (self.device_name, e))

    def get_info(self, exec_commands=()):
        # to decide  what commands will be using
        if exec_commands:
            commands = exec_commands
        elif self.commands:
            commands = self.commands
        else:
            return print("There is not commands to run!!!")
        if not isinstance(exec_commands, list):
            print("The command must put into a list!!")
            return False
        # execute the commands
        for command in commands:
            return self.connection.send_command(command)

    def get_info_and_write_into_separate_file(self, exec_commands=()):
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

    def __init__(self, devices_info, commands=[]):
        super(InterfaceTools, self).__init__(devices_info, commands)

    def get_all_interface(self):
        interfaces = []
        for line in self.get_info(["show ip int b"]).splitlines()[1:]:
            interfaces.append(re.split(r"\s+", line)[0])
        return interfaces

    def get_cdp_neighbors_information(self):
        neighbor_information = defaultdict(list)
        for neighbor_entry in (neighbor_entrys.split()
                               for neighbor_entrys in self.get_info(["show cdp neighbor"]).splitlines()[5:]):
            neighbor_information[neighbor_entry[1] + neighbor_entry[2]].append(neighbor_entry[0]+"-"+neighbor_entry[-2]+neighbor_entry[-1])
        return neighbor_information

    def get_unused_interfaces(self):
        pattern = re.compile(r"(\d+/\d+)")
        # get all interface but not include loopback interface
        interfaces = [interface for interface in self.get_all_interface() if "Loop" not in interface]
        # get the interface that has cdp neighbor
        cdp_interfaces = [pattern.findall(interface) for interface in self.get_cdp_neighbors_information().keys()]
        # compare to the all interface and the cdp interface then get the unused interface.
        unused_interface = [interface for interface in interfaces if pattern.findall(interface) not in cdp_interfaces]
        return unused_interface

    def get_used_interface(self):
        all_interfaces = self.get_all_interface()
        unused_interfaces = self.get_unused_interfaces()
        # return [interface for interface in all_interfaces if interface not in unused_interfaces]
        # or
        return list(set(all_interfaces)-set(unused_interfaces))

    def no_shutdown_all_interface(self):
        for interface in self.get_all_interface():
            commands = ["interface %s \n" % interface, "no shutdown"]
            print(self.connection.send_config_set(commands))

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

    def shutdown_unused_interface(self):
        unused_interface = self.get_unused_interfaces()
        shutdown_commands = []
        for interface in unused_interface:
            shutdown_commands += ["interface " + interface, "shutdown","exit"]
        return self.connection.send_config_set(shutdown_commands)

    def config_init_connection_ip(self):
        pass


class InformationTools(BaseConnection):
    """
    This is the class, that will get the device information from the device. The information support will be:
    The routing table information including the protocols and the total entrys in routing table.
    The mac address table, the arp table.
    The cpu and the memory utilize.    
    """
    def __init__(self, devices_info, commands=[]):
        super(InformationTools, self).__init__(devices_info, commands)

    def get_routing_protocol(self):
        pattern = re.compile(r"\"(.*?)\"",flags=re.DOTALL)
        info = self.get_info(exec_commands=["show ip protocols"])
        running_protocols = pattern.findall(info)
        return running_protocols if running_protocols else None

    def get_routing_entry(self):
        pattern = re.compile(r"\w+\s+(\d+\.\d+\.\d+\.\d+/\d+)")
        info = self.get_info(exec_commands=["show ip route"])
        routing_entry = list(dedupe(pattern.findall(info)))
        print(routing_entry)
        return routing_entry if routing_entry else None

    def get_arp_num(self):
        pass


