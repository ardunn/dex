import os


def initiate_editor(path):
    os.system(f"$EDITOR \"{path}\"")


class AttrDict(dict):
    """ Syntax candy """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
