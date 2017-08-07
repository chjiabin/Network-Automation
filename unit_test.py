import unittest
import netmiko
from base_tools import get_username_and_password, get_command, load_info_from_json, print_the_splitlines
from network_tools import BaseConnection, InterfaceTools, InformationTools

JsonFileName = "UnitTestDevices.json"
username, password = get_username_and_password()
commands = get_command("router-command.txt")
devices_information = load_info_from_json(JsonFileName)
devices_connections_information = load_info_from_json("Connection Information.json")


TestInterfaceTools_Devices = [InterfaceTools(
                              devices_info=device,
                              commands=commands,
                              connection_information=device_connection)
                              for (device, device_connection)
                              in zip(devices_information.values(), devices_connections_information.values())
                              ]

TestInformationTools_Devices = [InformationTools(
                                devices_info=device,
                                commands=commands)
                                for device in devices_information.values()]


class TestInterfaceTools(unittest.TestCase):

    @print_the_splitlines
    def setUp(self):
        self.devices = TestInterfaceTools_Devices
    """
    @print_the_splitlines
    def test_get_interface_info(self):
        for device in self.devices:
            print("testing get_all_interface %s" % device.device_name)
            print(device.get_all_interface())
            print("testing unused_interface %s" % device.device_name)
            print(device.get_unused_interfaces())
            print("testing used_interface %s" % device.device_name)
            print(device.get_used_interface())

    @print_the_splitlines
    def test_get_cdp_neighbors_information(self):
        for device in self.devices:
            print("testing get_cdp %s" % device.device_name)
            print(device.get_cdp_neighbors_information())

    @print_the_splitlines
    def test_load_interface_ip_address_commands(self):
        for device in self.devices:
            print("testing load_interface_ip_address_commands %s" % device.device_name)
            print(device.load_interface_ip_address_commands())
    """
    @print_the_splitlines
    def test_do_add_ip_address_to_interface(self):
        for device in self.devices:
            print("testing do_add_ip_address_to_interface %s" % device.device_name)
            print(device.do_add_ip_address_to_interface())


class TestInformationTools(unittest.TestCase):
    @print_the_splitlines
    def setUp(self):
        self.devices = TestInformationTools_Devices

    @print_the_splitlines
    def test_get_routing_protocol(self):
        for device in self.devices:
            print("testing get_routing_protocol %s" % device.device_name)
            protocols = device.get_routing_protocol()
            self.assertTrue(protocols)
            print(protocols)

    @print_the_splitlines
    def test_init(self):
        for device in self.devices:
            print("testing init %s" % device.device_name)
            self.assertTrue(isinstance(device.connection, netmiko.cisco.cisco_ios.CiscoIosBase))
            print("testing init %s successful.." % device.device_name)

    @print_the_splitlines
    def test_get_routing_entry(self):
        for device in self.devices:
            print("testing get_routing_entry %s" % device.device_name)
            routing_entry = device.get_routing_entry()
            self.assertTrue(routing_entry)
            print(routing_entry)

if __name__ == '__main__':
    unittest.main()