from . import exceptions

import sys

def yesno(question, default="no"):
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

def parse_vault_uri(path):
    res = path.split('/')
    if len(res) <= 1:
        raise exceptions.InvalidPathError(path)

    return {
        'mountpoint': res[0],
        'path': '/'.join(res[1:])
    }

def is_valid_mountpoint(client, mountpoint):
    try:
        client.secrets.kv.v2.read_configuration(mount_point=mountpoint)
        return True
    except:
        return False

def join_paths(*args):
    return '/'.join(
        arg.strip('/')
        for arg in args
    )
