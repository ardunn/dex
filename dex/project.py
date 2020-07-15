import os
import random
import copy
from typing import List, Union
from collections import namedtuple

from dion.task import Task
from dion.constants import done_str, status_primitives, priority_primitives, notes_dir_str, \
    task_extension, print_separator
from dion.util import process_name, AttrDict
from dion.exceptions import FileOverwriteError
from dion.logic import order_task_collection


class Project:
    def __init__(self, path: str
        self.path = path
        self.id = id
        self.name = None
        self.prefix_path = None
        self.notes_dir = None
        self.done_dir = None