import os
import re
import copy
from typing import Union

from dionysus.constants import priorities_pretty, statuses_pretty, task_extension, priority_primitives, status_primitives, all_delimiters, mdv
from dionysus.exceptions import FileTypeError, StatusError, PriorityError
from dionysus.util import initiate_editor


class Task:
    def __init__(self, path: str, id: int) -> None:
        """
        Task is a single task.

        Args:
            path (str): The full pathname of the file corresponding to this task.
            id (int): The unique task id.
        """
        self.path = path
        self.relative_path = None
        self.name = None
        self.id = id
        self.priority = None
        self.status = None
        self.content = None
        self._refresh()

    @classmethod
    def create_from_spec(cls, path_prefix, name, id, priority, status):
        path = os.path.join(path_prefix, f"{priority}{status} {name}{task_extension}")
        initiate_editor(path)
        return Task(path, id)

    # todo: turn this into a decorator
    def _refresh(self) -> None:
        self.prefix_path = os.path.dirname(self.path)
        relative_path = os.path.relpath(self.path, self.prefix_path)

        if relative_path.endswith(task_extension):
            statuses_in_path = [s in relative_path for s in statuses_pretty]
            n_statuses = sum(statuses_in_path)

            if n_statuses == 1:
                status = status_primitives[statuses_in_path.index(True)]
                priorities_in_path = [p in relative_path for p in priorities_pretty]
                n_priorities = sum(priorities_in_path)
                if n_priorities == 1:
                    priority = priority_primitives[priorities_in_path.index(True)]
                else:
                    print(priorities_in_path)
                    raise PriorityError(f"Task {relative_path} in {self.prefix_path} has {n_priorities} priorities. Each task must have one priority. Valid priorities are {priorities_pretty}")
            else:
                raise StatusError(f"Task {relative_path} in {self.prefix_path} has {n_statuses} statuses. Each task must have one status. Valid statuses are {statuses_pretty}")
        else:
            raise FileTypeError(f"Task {relative_path} in {self.prefix_path} has invalid extension. Valid extensions are {task_extension}")

        name = copy.deepcopy(relative_path)
        for replace in [str(priority), status, task_extension]:
            name = name.replace(replace, "")
        self.name = name.strip()
        self.relative_path = relative_path
        self.status = status
        self.priority = priority

        with open(self.path, 'r') as f:
            self.content = f.read()

    def set_status(self, new_status: str) -> None:
        if new_status not in status_primitives:
            raise StatusError(f"Invalid new status {new_status}. Valid statuses are {status_primitives}")
        else:
            new_status_str = qualifier_converter(to_list=statuses_pretty, from_list=status_primitives, key=new_status)
            old_status_str = qualifier_converter(to_list=statuses_pretty, from_list=status_primitives, key=self.status)
            new_relpath = self.relative_path.replace(old_status_str, new_status_str)


            is_complete = new_status == status_primitives[-1]
            was_complete = self.status == status_primitives[-1]

            if is_complete and not was_complete:
                done_dir = os.path.join(self.prefix_path, "done")
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
        
    def rename(self, new_name: str) -> None:
        if any([delim in new_name for delim in all_delimiters]):
            raise 
        new_relpath = self.relative_path.replace(self.name, new_name)
        new_path = self.os.path.join(self.prefix_path, new_relpath)
        os.rename(self.path, new_path)
        self.path = new_path
        self._refresh()

    def set_priority(self, new_priority: int):
        if self.priority not in priority_primitives:
            raise PriorityError(f"Priority {new_priority} invalid. Valid priorities are {priority_primitives}")
        else:
            new_priority_str = qualifier_converter(to_list=priorities_pretty, from_list=priority_primitives, key=new_priority)
            old_priority_str = qualifier_converter(to_list=priorities_pretty, from_list=priority_primitives, key=self.priority)
            new_relative_path = self.relative_path.replace(old_priority_str, new_priority_str)
            new_path = os.path.join(self.prefix_path, new_relative_path)
            os.rename(self.path, new_path)
            self.path = new_path
            self._refresh()

    def view(self):
        formatted = mdv.main(self.content)
        print(formatted)

    def edit(self) -> None:
        initiate_editor(self.path)
        self._refresh()


def qualifier_converter(to_list, from_list, key):
    print(from_list)
    print(key)
    return to_list[from_list.index(key)]


if __name__ == "__main__":
    t = Task("/home/x/dionysus/dionysus/tmp/{1}[todo] some cool task.md", id=1)

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

    t.view()