# from getpass import getpass
import os
import json


def get_username_and_password():
    username = "cisco"
    pass1 = "cisco"
    pass2 = "cisco"
    if pass1 != pass2:
        print("The password you enter do not match!")
        return False
    else:
        password = pass1
        return username, password


def get_command(command_file_name):
    """get the command from a file"""
    if os.path.exists(command_file_name):
        with open(command_file_name) as fl:
            return [line for line in fl.readlines() if line != "\n"]
    else:
        print("commands file do not exists!")


def write_to_the_file(dst_location, lines):
    with open(dst_location, "w") as fl:
        fl.writelines(lines)
    return True


def dedupe(items):
    """This is a method to delete the same items in a list and keep the sequence."""
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


# Read the devices information from a file, should be written in JSON
def load_info_from_json(file_name):
    with open(file_name, encoding='utf-8') as f:
        return json.load(f)


def print_the_splitlines(fun):
    def inner(*args, **kw):
        print("~" * 79)
        fun(*args, **kw)
    return inner
