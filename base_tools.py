# from getpass import getpass
import os


def get_username_and_password():
    username = "cisco"
    pass1 = "cisco"
    pass2 = "cisco"
    if pass1 != pass2:
        print("The password you enter do not match!")
        return False
    else:
        password = pass1
        return (username, password)


def get_command(command_file_name):
    """get the command from a file"""
    if os.path.exists(command_file_name):
        with open(command_file_name) as fl:
            commands = [line for line in fl.readlines() if line != "\n"]
    else:
        print("commands file do not exists!")
    return commands


def write_to_the_file(dst_location, lines):
    with open(dst_location, "w") as fl:
        fl.writelines(lines)
    return True
