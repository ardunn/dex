import os

from dex.constants import editor


def initiate_editor(path):
    os.system(f"{editor} \"{path}\"")