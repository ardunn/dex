import os

from dionysus.task import Task
from dionysus.constants import done_str, notes_dir_str, tasks_dir_str
from dionysus.util import process_name
from dionysus.exceptions import FileOverwriteError


class Project:
    def __init__(self, path: str, id: str):
        self.path = path
        self.id = id

        self.name = None
        self.prefix_path = None
        self.tasks_dir = None
        self.notes_dir = None
        self.done_dir = None

    @classmethod
    def create_from_spec(cls, id: str, path_prefix: str, name: str, init_notes: bool = True):
        name = process_name(name)
        id = process_id(id)

        dest_dir = os.path.join(path_prefix, name)
        if os.path.exists(dest_dir):
            raise FileOverwriteError(f"Project \'{name}\' already exists: \'{dest_dir}\'")
        else:
            tasks_dir = os.path.join(dest_dir, tasks_dir_str)
            os.makedirs(tasks_dir)

        done_dir = os.path.join(dest_dir, done_str)
        if not os.path.exists(done_dir):
            os.mkdir(done_dir)
        if init_notes:
            notes_dir = os.path.join(dest_dir, notes_dir_str)
            if os.path.exists(notes_dir):
                os.mkdir(notes_dir)
        else:
            notes_dir = None

        return Project(dest_dir, id)

    def _refresh(self):
        self.prefix_path = os.path.dirname(self.path)
        self.name = os.path.dirname(self.path).split("/")[-1]
        self.tasks_dir = os.path.join(self.prefix_path, tasks_dir_str)  # must exist
        self.done_dir = os.path.join(self.tasks_dir, done_str)          # ok if this doesn't exist
        notes_dir = os.path.join(self.prefix_path, notes_dir_str)

        if not os.path.exists(notes_dir):
            notes_dir = None
        self.notes_dir = notes_dir

        if not os.path.exists(self.tasks_dir):
            os.mkdir(self.tasks_dir)

    @property
    def tasks(self):
        tasks = []
        for f in os.listdir(self.path):
            fp = os.path.join
            t = Task(path=f)
            tasks.append(t)

    def rename(self, new_name):
        name = process_name(name)


    def work(self):
        # return high priority tasks
        pass

    def stats(self):
        pass

    def prioritize(self):
        pass

    def deprioritize(self):
        pass

    def list_tasks(self):
        # list tasks and their ids
        pass


def process_id(id: str) -> str:
    if len(id) == 1:
        return id.lower()
    else:
        raise ValueError("Project Ids must be a length 1 string.")
