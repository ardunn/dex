import os
import re
import copy
from typing import Iterable

from dion.constants import priorities_pretty, statuses_pretty, task_extension, priority_primitives, status_primitives, all_delimiters, mdv, done_str, todo_str, doing_str, hold_str
from dion.exceptions import FileTypeError, StatusError, PriorityError, FileOverwriteError
from dion.util import initiate_editor, process_name


class Task:
    def __init__(self, path: str, id: int) -> None:
        """
        Task is a single task.

        Args:
            path (str): The full pathname of the file corresponding to this task.
            id (str): The unique project + task id, e.g. "a1".
        """
        self.path = path
        self.relative_path = None
        self.name = None
        self.id = id
        self.priority = None
        self.status = None
        self.content = None
        self._refresh()

    def __str__(self):
        return f"<dion Task {self.id}: ({self.priority} {self.status}) - [{self.name}]>"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def create_from_spec(cls, id: str, path_prefix: str, name: str, priority: int, status: str, edit: bool = True):
        check_status(status)
        check_priority(priority)

        if status == done_str:
            raise StatusError("Cannot create a done task. It's already done, stop wasting time.")
        name = process_name(name)
        status_pretty = qualifier_converter(to_list=statuses_pretty, from_list=status_primitives, key=status)
        priority_pretty = qualifier_converter(to_list=priorities_pretty, from_list=priority_primitives, key=priority)
        path = os.path.join(path_prefix, f"{priority_pretty}{status_pretty} {name}{task_extension}")
        if os.path.exists(path):
            raise FileOverwriteError(f"The file \'{path}\' already exists.")
        if edit:
            initiate_editor(path)
        else:
            with open(path, "w") as f:
                f.write(f"Task {id}: {name}")
        t = Task(path, id)
        # prevent done tasks from not being placed in done folder,
        # in the weird case the status was done when it was created from spec
        # t.set_status(status)
        return t

    def _refresh(self) -> None:
        if os.path.isdir(self.path):
            raise FileTypeError("Task cannot be directory!")
        self.prefix_path = os.path.dirname(self.path)
        relative_path = os.path.relpath(self.path, self.prefix_path)

        if relative_path.endswith(task_extension):
            statuses_in_path = [s in relative_path for s in statuses_pretty]
            n_statuses = sum(statuses_in_path)

            if n_statuses == 1:
                status = qualifier_converter(status_primitives, statuses_in_path, True)
                priorities_in_path = [p in relative_path for p in priorities_pretty]
                n_priorities = sum(priorities_in_path)
                if n_priorities == 1:
                    priority = qualifier_converter(priority_primitives, priorities_in_path, True)
                else:
                    raise PriorityError(f"Task \'{relative_path}\' in \'{self.prefix_path}\' has {n_priorities} priorities. Each task must have one priority. Valid priorities are {priorities_pretty}")
            else:
                raise StatusError(f"Task \'{relative_path}\' in \'{self.prefix_path}\' has {n_statuses} statuses. Each task must have one status. Valid statuses are {statuses_pretty}")
        else:
            raise FileTypeError(f"Task \'{relative_path}\' in \'{self.prefix_path}\' has invalid extension. Valid extensions are \'{task_extension}\'")

        name = copy.deepcopy(relative_path)
        for replace in [str(priority), status, task_extension] + list(all_delimiters):
            name = name.replace(replace, "")
        self.name = process_name(name)
        self.relative_path = relative_path
        self.status = status
        self.priority = priority

        with open(self.path, 'r') as f:
            self.content = f.read()

    def set_status(self, new_status: str) -> None:
        check_status(new_status)
        new_status_str = qualifier_converter(to_list=statuses_pretty, from_list=status_primitives, key=new_status)
        old_status_str = qualifier_converter(to_list=statuses_pretty, from_list=status_primitives, key=self.status)
        new_relpath = self.relative_path.replace(old_status_str, new_status_str)
        is_complete = new_status == done_str
        was_complete = self.status == done_str

        if is_complete and not was_complete:
            done_dir = os.path.join(self.prefix_path, done_str)
            if not os.path.exists(done_dir):
                os.mkdir(done_dir)
            new_path = os.path.join(done_dir, new_relpath)
        elif was_complete and not is_complete:
            # assuming the directory isn't goofed up
            new_path = os.path.join(self.prefix_path, f"../{new_relpath}")
        else:
            # it's going to not move from the folder it's in
            # if it is done, it will stay there
            # if it is not done, it will stay there
            new_path = os.path.join(self.prefix_path, new_relpath)
        os.rename(self.path, new_path)
        self.path = new_path
        self._refresh()

    def set_priority(self, new_priority: int) -> None:
        check_priority(new_priority)
        new_priority_str = qualifier_converter(to_list=priorities_pretty, from_list=priority_primitives, key=new_priority)
        old_priority_str = qualifier_converter(to_list=priorities_pretty, from_list=priority_primitives, key=self.priority)
        new_relative_path = self.relative_path.replace(old_priority_str, new_priority_str)
        new_path = os.path.join(self.prefix_path, new_relative_path)
        os.rename(self.path, new_path)
        self.path = new_path
        self._refresh()
        
    def rename(self, new_name: str) -> None:
        new_name = process_name(new_name)
        new_relpath = self.relative_path.replace(self.name, new_name)
        new_path = os.path.join(self.prefix_path, new_relpath)
        os.rename(self.path, new_path)
        self.path = new_path
        self._refresh()

    def view(self) -> None:
        formatted = mdv.main(self.content)
        print(formatted)

    def edit(self) -> None:
        initiate_editor(self.path)
        self._refresh()

    def work(self):
        self.set_status(doing_str)

    def complete(self):
        self.set_status(done_str)

    def put_on_hold(self):
        self.set_status(hold_str)

    @property
    def hold(self):
        return self.status == hold_str

    @property
    def done(self):
        return self.status == done_str

    @property
    def doing(self):
        return self.status == doing_str

    @property
    def todo(self):
        return self.status == todo_str

    @property
    def modification_time(self):
        return os.path.getmtime(self.path)


def qualifier_converter(to_list, from_list, key) -> Iterable:
    return to_list[from_list.index(key)]


def check_priority(priority: int) -> None:
    if priority not in priority_primitives:
        raise PriorityError(f"Priority {priority} invalid. Valid priorities are {priority_primitives}")


def check_status(status: str) -> None:
    if status not in status_primitives:
        raise StatusError(f"Invalid new status {status}. Valid statuses are {status_primitives}")


if __name__ == "__main__":
    # t = Task("/home/x/dion/dion/tmp/{1}[todo] some cool task.md", id=1)

    t = Task.create_from_spec(
        id="b3",
        path_prefix="/home/x/dion/dion/tmp",
        name="new spec created from something else2   ",
        priority=3,
        status="todo",
    )

    print(t)

    for attr in ["status", "priority", "relative_path", "path", "name", "id",
                 # "content"
                 ]:
        a = getattr(t, attr)
        # print(attr, "||||", a, type(a))

    # t.set_status("done")
    # t.edit()
    # t.set_status("todo")

    # t.set_priority(3)
    # t.edit()
    # t.set_priority(1)

    # t.view()

    # t.rename("  a different cool task ")
    # t.edit()
    # t.rename("some cool task")
