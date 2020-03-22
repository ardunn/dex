import os
import sys

from dion.constants import editor, all_delimiters
from dion.exceptions import FileCharacterError

if sys.platform.lower() == "win32":
    os.system('color')


class AttrDict(dict):
    """ Syntax candy """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def process_name(name: str) -> str:
    """
    General path name processing.

    Args:
        name:

    Returns:

    """
    if any([delim in name for delim in all_delimiters]):
        raise FileCharacterError(f"The characters {all_delimiters} are not allowed in dion filenames.")
    else:
        return name.strip()


def initiate_editor(path):
    os.system(f"{editor} \"{path}\"")


# Group of Different functions for different styles
class Style():
    def __init__(self):
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        yellow = '\033[33m'
        blue = '\033[34m'
        magenta = '\033[35m'
        cyan = '\033[36m'
        white = '\033[37m'
        underline = '\033[4m'
        reset = '\033[0m'
        self.colormap = {
            "k": black,
            "r": red,
            "y": yellow,
            "g": green,
            "b": blue,
            "m": magenta,
            "c": cyan,
            "w": white,
            "u": underline,
            "x": reset,
        }

    def format(self, color, string_to_format):
        return self.colormap[color] + string_to_format + self.colormap["x"]


if __name__ == "__main__":
    style = Style()
    print(style.format("y", "Hello, ") + style.format("x", "World!"))
