import os
import datetime
import copy
from typing import List
import warnings

from dex.util import AttrDict

from dex.note import Note
from dex.task import Task
from dex.constants import abandoned_str, done_str, inactive_subdir, status_primitives, tasks_subdir, notes_subdir, \
    valid_project_ids, task_extension, note_extension
from dex.exceptions import DexException, FileOverwriteError


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
        self.inactive_dir = os.path.join(self.tasks_dir, inactive_subdir)

    def __str__(self):
        n_tasks = len(self.tasks.all)
        return f"<dex Project {self.id}: [{self.name}] ({n_tasks} tasks)>"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_files(cls, path: str, id: str, coerce_pid_mismatches=False):
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

        for task in tasks:
            project_id = task.dexid[0]
            number_task_id = int(task.dexid[1:])
            if project_id != id:
                warnings.warn(
                    f"Task {task.dexid} does not have project id matching project {id}: {path}."
                )
                if coerce_pid_mismatches:
                    warnings.warn(f"Converting task {task.dexid} to project {id}!")
                    task.set_dexid(f"{id}{number_task_id}")

        for fn in os.listdir(notes_dir):
            n_full = os.path.abspath(os.path.join(notes_dir, fn))
            if n_full.endswith(note_extension):
                n = Note.from_file(n_full)
                notes.append(n)

        return cls(path, id, tasks, notes)

    @classmethod
    def new(cls, path: str, id: str):
        """
        Create a project object

        Args:
            path: The path of the new project
            *args, **Kwargs: Args and kwards for Task

        Returns:
            Project object, with the required directories created
        """
        for subdir in (tasks_subdir, notes_subdir):
            full_subdir = os.path.join(path, subdir)
            if not os.path.exists(full_subdir):
                os.makedirs(full_subdir)
            if subdir == tasks_subdir:
                full_inactive_subdir = os.path.join(full_subdir, inactive_subdir)
                if not os.path.exists(full_inactive_subdir):
                    os.makedirs(full_inactive_subdir)
        return cls(path, id, tasks=[], notes=[])

    def rename(self, new_name: str) -> None:
        """
        Rename a project. Should be used atomically (i.e., called, then object remade using .from_files()

        Args:
            new_name (str): The name of the new project.

        Returns:
            None
        """

        # todo: this must be used atomically, as the states of all tasks will differ from files after...
        containing_folder = os.path.join(self.path, os.pardir)
        new_path = os.path.join(containing_folder, new_name)
        os.rename(self.path, new_path)
        self.path = new_path

    def create_new_task(self, name: str,
                        effort: int,
                        due: datetime.datetime,
                        importance: int,
                        status: str,
                        flags: list,
                        edit_content: bool = False
                        ) -> Task:
        """
        Can be used non atomically. Arguments are mostly the same as for Task.

        Args:
            name (str): The name of the new task. Will be converted to a path by Project for use with Task.
            effort:
            due:
            importance:
            status:
            flags:
            edit_content:

        Returns:
            Task (the created task).
        """

        fname = name + task_extension
        path = os.path.join(os.path.join(self.path, tasks_subdir), fname)

        if status in (abandoned_str, done_str):
            raise DexException("Cannot make a new task with an initially inactive status!")

        if path in [t.path for t in self.tasks.all]:
            raise FileOverwriteError(f"Task already exists with the name: {name}")

        all_task_numbers = [int(copy.deepcopy(t.dexid).replace(self.id, "")) for t in self._tasks]
        max_task_numbers = max(all_task_numbers) if all_task_numbers else 0
        new_task_number = max_task_numbers + 1
        new_task_id = f"{self.id}{new_task_number}"
        t = Task.new(new_task_id, path, effort, due, importance, status, flags, edit_content=edit_content)
        self._tasks.append(t)
        return t

    def create_new_note(self, *args, **kwargs) -> Note:
        pass


    @property
    def tasks(self):
        """
        A dictionary/class of tasks, organized by status. E.g., self.tasks.done

        Returns:
            task_collection (AttrDict): A dict/attr collection of [Task] lists, corresponding to different status
                primitives. Also includes a key for "all", which is an unordered list of all tasks.

        """
        # priority_dict = {priority: [] for priority in priority_primitives}
        task_dict = {status: [] for status in status_primitives}
        task_dict["all"] = self._tasks
        task_collection = AttrDict(task_dict)

        for t in task_dict["all"]:
            task_dict[t.status].append(t)
        return task_collection


    @property
    def task_map(self):
        return {t.dexid: t for t in self.tasks.all}


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
