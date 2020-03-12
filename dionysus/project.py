import os
import random
from typing import List
from collections import namedtuple

from dionysus.task import Task
from dionysus.constants import done_str, status_primitives, priority_primitives, notes_dir_str, tasks_dir_str, task_extension, print_separator
from dionysus.util import process_name, AttrDict
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
            if not os.path.exists(notes_dir):
                os.mkdir(notes_dir)

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

    def rename(self, new_name):
        new_name = process_name(new_name)
        new_path = os.path.join(self.prefix_path, new_name)
        self.path = new_path
        os.rename(self.path, new_path)
        self._refresh()

    def set_task_priorities(self, priority):
        for task in self.tasks.all:
            task.set_priority(priority)
        self._refresh()

    def new_task(self) -> None:
        Task(self.prefix_path, id=99999)
        self._refresh()

    @property
    def tasks(self) -> List:
        """
        A dictionary/class of tasks
        Returns:

        """
        # priority_dict = {priority: [] for priority in priority_primitives}
        task_dict = {status: [] for status in status_primitives}
        task_dict["all"] = []
        task_collection = AttrDict(task_dict)
        # tasks = []
        unique_id = 0
        for container_dir in [self.tasks_dir, self.done_dir]:
            for f in os.listdir(container_dir):
                fp = os.path.join(container_dir, f)
                if fp.endswith(task_extension):
                    unique_id += 1
                    t = Task(path=fp, id=unique_id)
                    task_collection[t.status].append(t)
        return task_collection




    def list_tasks(self):
        print(f"\n{print_separator}\nProject {self.name}\n{print_separator}")
        pass

    def work(self):
        # return high priority tasks
        pass


def process_id(id: str) -> str:
    if len(id) == 1:
        return id.lower()
    else:
        raise ValueError("Project Ids must be a length 1 string.")


def order_task_collection(task_collection: AttrDict, limit=0, include_done=False) -> List[Task]:
    """

    Order a task collection

    1. deprioritize done
    2. deprioritize hold
    3. priority ordering
    4. doing > todo
    5. ordering based on last edited/most worked on OR random

    Args:
        task_collection:

    Returns:

    """

    # most important is low index
    ordered = []
    if include_done:
        done_ordered = sorted(task_collection.done, key=lambda t: t.priority)
        ordered = done_ordered

    hold_ordered = sorted(task_collection.hold, key=lambda t: t.priority)
    ordered = hold_ordered + ordered

    todoing = task_collection.todo + task_collection.doing

    # more advanced ordering for to-do + doing
    todoing_by_priority = {priority: [] for priority in priority_primitives}
    for t in todoing:
        todoing_by_priority[t.priority].append(p)
    # to-doing segregated by priority level, priority levels decreasing
    todoing_by_priority = sorted([(p, tc) for p, tc in todoing_by_priority.items()], key=lambda x: x[0], reverse=True)

    for _, tc in todoing_by_priority:
        # doing has higher priority (lower index) than to-do within a given priority level
        plevel_doing = [t for t in tc if t.doing]
        plevel_todo = [t for t in tc if t.todo]

        #todo: could add a rule for sorting based on time worked/last edited
        #todo: for now, just randomly shuffles tasks with identical priority and identical todo or doing status
        random.shuffle(plevel_doing)
        random.shuffle(plevel_todo)
        plevel_ordered = plevel_doing + plevel_todo
        ordered = plevel_ordered + ordered
    return ordered



if __name__ == "__main__":
    p = Project.create_from_spec(
        id="a",
        path_prefix="/home/x/dionysus/dionysus/tmp_projset",
        name="proj1"
    )

    print