import os
import random
import datetime
import copy
from typing import List, Union
from collections import namedtuple

from dex.task import Task
from dex.util import AttrDict

from dex.note import Note
from dex.task import Task
from dex.constants import inactive_subdir, status_primitives, tasks_subdir, notes_subdir, valid_project_ids, task_extension, note_extension
# from dex.util import process_name, AttrDict
from dex.exceptions import DexcodeException, FileOverwriteError
# from dex.logic import order_task_collection


class Project:
    def __init__(self, path: str, id: str, tasks: List[Task], notes: List[Note]):

        if not os.path.isdir(path):
            os.makedirs(path)

        self.path = os.path.abspath(path)
        self.id = process_project_id(id)

        self.name = os.path.basename(self.path)

        self._tasks = tasks
        self._notes = notes

        self.notes_dir = os.path.join(self.path, notes_subdir)
        self.tasks_dir = os.path.join(self.path, tasks_subdir)
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

        path = os.path.abspath(path)
        tasks_dir = os.path.join(path, tasks_subdir)
        notes_dir = os.path.join(path, notes_subdir)
        inactive_dir = os.path.join(tasks_dir, inactive_subdir)

        for subdir in (notes_dir, inactive_dir):
            if not os.path.exists(subdir):
                os.makedirs(subdir, exist_ok=False)

        for taskdir in (tasks_dir, inactive_dir):
            for ft in os.listdir(taskdir):
                f_full = os.path.abspath(os.path.join(taskdir, ft))
                if f_full.endswith(task_extension):
                    t = Task.from_file(f_full)
                    tasks.append(t)

        for fn in os.listdir(notes_dir):
            n_full = os.path.abspath(os.path.join(notes_dir, fn))
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
        new_path = os.path.join(self.path, new_name)
        os.rename(self.path, new_path)
        self.path = new_path

    def create_new_task(self, dexid: str, path: str, effort: int, due: datetime.datetime, importance: int, status: str,
                 flags: list, edit_content: bool = False) -> Task:

        if path in [t.path for t in self.tasks.all]:
            raise FileOverwriteError(f"Task already exists with the name: {name}")

        all_task_numbers = [int(copy.deepcopy(t.id).replace(self.id, "")) for t in self.tasks.all]
        max_task_numbers = max(all_task_numbers) if all_task_numbers else 0
        new_task_number = max_task_numbers + 1
        new_task_id = f"{self.id}{new_task_number}"
        t = Task.create_from_spec(new_task_id, self.path, name, priority, status, edit=edit)
        return t

    def create_new_note(self, *args, **kwargs) -> Note:
        pass

    def get_n_highest_priority_tasks(self):
        pass


    @property
    def tasks(self):
        """
        A dictionary/class of tasks
        Returns:

        """
        # priority_dict = {priority: [] for priority in priority_primitives}
        task_dict = {status: [] for status in status_primitives}
        task_dict["all"] = self._tasks
        task_collection = AttrDict(task_dict)
        unique_id = 0

        for t in task_dict["all"]:



        for container_dir in [self.done_dir, self.path]:
            for f in os.listdir(container_dir):
                fp = os.path.join(container_dir, f)
                if os.path.exists(fp):
                    if fp.endswith(task_extension):
                        unique_id += 1
                        pid_tid = f"{self.id}{unique_id}"
                        t = Task(path=fp, id=pid_tid)
                        task_collection[t.status].append(t)
                        task_collection["all"].append(t)
        return task_collection


    @property
    def task_map(self):
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
