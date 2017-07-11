from getpass import getpass


def get_username_and_password():
    username = input("Please enter your username:")
    pass1 = getpass("Please enter your password:")
    pass2 = getpass("Please verify your password:")
    if pass1 != pass2:
        print("The password you enter do not match!")
        return False
    else:
        password = pass1
        return (username, password)
