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
                commands_output = self.get_info(tuple(commands))
                file_name = str(commands).replace(" ", "_")
                print("writing to the file " + file_name)
                if commands_output:
                    write_to_the_file(".\%s\%s.txt" % (self.prompt, file_name), commands_output)

    def config(self, commands):
        try:
            print(self.connection.send_config_set(commands))
        except Exception as e:
            print("Some error happened for the reason %s..." % e)
            return None
        else:
            return True


class InterfaceTools(BaseConnection):
    """
    This module providing some functions that involved with interfaces 
    like shutdown all interface
    undo shutdown all interface
    shutdown interface that is no in using 
    make description for interface by checking the cdp neighbor.
    """

    def __init__(self, devices_info, commands=(), connection_information=()):
        super(InterfaceTools, self).__init__(devices_info, commands)
        # using for descript the IP address connection between devices.
        # if none using default way to make ip address connection.
        self.connection_information = connection_information if connection_information else None

    def get_all_interface(self):
        interfaces = []
        for line in self.get_info(["show ip int b"]).splitlines()[1:]:
            interfaces.append(re.split(r"\s+", line)[0])
        return interfaces

    def get_cdp_neighbors_information(self):
        """
        The return values will be like:
        defaultdict(<class 'list'>,
         {
        'Eth3/0': ['R4.cisco.com-Eth3/0', 'R2.cisco.com-Eth3/0', 'R1.cisco.com-Eth3/0'], 
        'Fas0/0': ['R4.cisco.com-Fas1/0'], 
        'Fas1/0': ['R2.cisco.com-Fas0/0']
        }
        )
        """
        # The defaultdict is a data structure that a dict item is another list or dicts.
        neighbor_information = defaultdict(list)
        for neighbor_entry in (neighbor_entrys.split()
                               for neighbor_entrys in self.get_info(["show cdp neighbor"]).splitlines()[5:]):
            key = neighbor_entry[1] + neighbor_entry[2]
            neighbor_information[key].append(neighbor_entry[0]+"-"+neighbor_entry[-2]+neighbor_entry[-1])
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

    def load_interface_ip_address_commands(self):
        commands = []
        if self.connection_information:
            for interface in self.connection_information.keys():
                commands.append(interface)
                ip_address_commands = "ip address " + \
                                      self.connection_information[interface]["Local_IP_Address"] +\
                                      " 255.255.255.0"
                commands.append(ip_address_commands)
        return commands

    def do_no_shutdown_all_interface(self):
        no_shutdown_all_interface_commands = []
        # making the commands
        for interface in self.get_all_interface():
            no_shutdown_all_interface_commands += ["interface %s \n" % interface, "no shutdown"]
        # if commands being execute successfully, will return True
        return self.config(no_shutdown_all_interface_commands)

    def do_make_neighbor_description(self):
        neighbor_information = self.get_cdp_neighbors_information()
        description_commands = []
        # making the commands
        for interface, neighbors in neighbor_information.items():
            interface_command = "interface " + interface
            neighbor_command = "description Connect_to-"
            for neighbor in neighbors:
                neighbor_command += "-"+neighbor
            description_commands += [interface_command, neighbor_command, "exit"]
        # if commands being execute successfully, will return True
        return self.config(description_commands)

    def do_shutdown_unused_interface(self):
        unused_interface = self.get_unused_interfaces()
        shutdown_commands = []
        # making the commands
        for interface in unused_interface:
            shutdown_commands += ["interface " + interface, "shutdown","exit"]
        # if commands being execute successfully, will return True
        return self.config(shutdown_commands)

    def do_add_ip_address_to_interface(self):
        # making the commands
        add_ip_address_to_interface_commands = self.load_interface_ip_address_commands()
        if add_ip_address_to_interface_commands:
            # if commands being execute successfully, will return True
            return self.config(add_ip_address_to_interface_commands)
        else:
            print("There is not connection information to add ip address to interface...,"
                  "Please provided the connection information in device hanlder...")


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
        no_protocols_running_warn = "There is no routing protocols running.."
        try:
            info = self.get_info(exec_commands=["show ip protocols"])
        except Exception as e:
            raise e
        finally:
            running_protocols = pattern.findall(info)
            return running_protocols if running_protocols else no_protocols_running_warn

    def get_routing_entry(self):
        pattern = re.compile(r"\w+\s+(\d+\.\d+\.\d+\.\d+/\d+)")
        info = self.get_info(exec_commands=["show ip route"])
        routing_entry = list(dedupe(pattern.findall(info)))
        return routing_entry if routing_entry else None

    def get_arp_num(self):
        pattern = re.compile("")
        info = self.get_info(exec_commands=["show ip arp"])
        pass

    def load_info_of_device(self):
        pass
