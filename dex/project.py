import os
import random
import copy
from typing import List, Union
from collections import namedtuple

from dex.task import Task
from dex.util import AttrDict

from dex.note import Note
from dex.task import Task
from dex.constants import inactive_subdir, status_primitives, notes_subdir, valid_project_ids, task_extension, note_extension
# from dex.util import process_name, AttrDict
from dex.exceptions import DexcodeException
# from dex.logic import order_task_collection


class Project:
    def __init__(self, path: str, id: str, tasks: List[Task], notes: List[Note]):

        self.path = path
        self.id = process_project_id(id)

        self._tasks = tasks
        self._notes = notes

        self.notes_dir = os.path.join(self.path, notes_subdir)
        self.inactive_dir = os.path.join(self.path, inactive_subdir)

    def __str__(self):
        n_tasks = len(self.tasks.all)
        return f"<dex Project {self.id}: [{self.name}] ({n_tasks} tasks)>"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_files(cls, path: str, id: str):
        tasks = []
        notes = []

        notes_dir = os.path.join(path, notes_subdir)
        inactive_dir = os.path.join(path, inactive_subdir)

        for subdir in (notes_dir, inactive_dir):
            if not os.path.exists(subdir):
                os.makedirs(subdir, exist_ok=False)

        for ft in os.listdir(path) + os.listdir(inactive_dir):
            f_full = os.path.abspath(os.path.join(os.curdir, ft))
            if f_full.endswith(task_extension):
                t = Task.from_file(f_full)
                tasks.append(t)
        for fn in os.listdir(notes_dir):
            n_full = os.path.abspath(os.path.join(os.curdir, fn))
            if n_full.endswith(note_extension):
                n = Note.from_file(n_full)
                notes.append(n)

        return cls(path, id, tasks, notes)

    def rename(self, new_name: str) -> None:
        """
        Rename a project. Should be used atomically (i.e., called, then object remade using .from_files()

        Args:
            new_name (str): The name of the new project.

        Returns:
            None
        """

        # todo: this must be used atomically, as the states of all tasks will differ from files after...
        new_path = os.path.join(self.prefix_path, new_name)
        os.rename(self.path, new_path)
        self.path = new_path

    def create_new_task(self, *args, **kwargs) -> Task:
        pass

    def create_new_note(self, *args, **kwargs) -> Note:
        pass

    @property
    def tasks(self):
        pass

    @property
    def task_map(self):
        pass

    def get_n_highest_priority_tasks(self):
        pass


def process_project_id(proj_id: str) -> str:
    """
    Ensure the project ID is valid.

    Args:
        proj_id (str): The candidate project id.

    Returns:
        proj_id (str): the processed project id.
    """
    proj_id = proj_id.lower()
    if proj_id not in valid_project_ids:
        raise ValueError(f"Project id must be single alphabetical character in lowercase: {valid_project_ids}")
    return proj_id
