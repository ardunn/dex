import os


def initiate_editor(path):
    os.system(f"$EDITOR \"{path}\"")


class AttrDict(dict):
    """ Syntax candy """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class TerminalStyle:
    """
    Styling of the terminal fonts.
    """
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
    colormap = {
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

    def f(self, color: str, string_to_format: str) -> str:
        """
        Format a string with color.

        Args:
            color (str): Letter code for the color
            string_to_format (str): The string to colorize

        Returns:
            Colorized string
        """
        return self.colormap[color] + string_to_format + self.colormap["x"]