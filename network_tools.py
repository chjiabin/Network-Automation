import netmiko


class interface_tools(object):
    """docstring for interface_tools"""

    def __init__(self, device_info):
        super(interface_tools, self).__init__()
        self.connection = netmiko.ConnectHandler(**device_info)

    def get_all_interface(self):
        interface_info = self.connection.send_command(
            "show ip int b").splitlines()[1:]
        return interface_info
