import os

from dionysus.constants import editor, all_delimiters
from dionysus.exceptions import FileCharacterError


def process_name(name: str) -> str:
    """
    General path name processing.

    Args:
        name:

    Returns:

    """
    if any([delim in name for delim in all_delimiters]):
        raise FileCharacterError(f"The characters {all_delimiters} are not allowed in dionysus filenames.")
    else:
        return name.strip()


def initiate_editor(path):
    os.system(f"{editor} \"{path}\"")
