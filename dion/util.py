import os

from dion.constants import editor, all_delimiters
from dion.exceptions import FileCharacterError


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
