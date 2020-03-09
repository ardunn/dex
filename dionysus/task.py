import os
import re

from dionysus.constants import status_regex, priority_regex, priority_keyword, status_mapping, status_mapping_inverted, task_extension, lsd, rsd, lpd, rpd, editor

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


    # todo: turn this into a decorator
    def _refresh(self) -> None:
        self.prefix_path = os.path.dirname(self.path)
        self.relative_path = os.path.relpath()
        name = self.relative_path

        status_match = re.search(status_regex, self.relative_path)
        if status_match:
            status_raw = status_match.groups()[0]
            if status_raw in status_mapping:
                self.status = status_mapping
                name = name \
                    .replace(lsd + status_raw + rsd, "") \
                    .replace(task_extension, "")
            else:
                raise ValueError(f"Task {self.path} has status {status_raw} which is not a valid mapping. Must use one of {list(status_mapping.keys())}")
        else:
            raise ValueError(f"Task {self.path} has no parsable status from regex {status_regex}")

        priority_match= re.search(priority_regex, self.relative_path)
        if priority_match:
            priority_raw = priority_match.groups()[0]
            if priority_raw == priority_keyword:
                self.priority = True
                name = name.replace(lpd + priority_raw + rpd, "")
            else:
                raise ValueError(f"Task {self.path} has priority {priority_raw} which is invalid. Must use {priority_keyword}")
        else:
            self.priority = False

        self.name = name.strip()

        with open(self.path, 'r') as f:
            self.content = f.read()

    def change_status(self, new_status: str) -> None:
        if new_status not in status_mapping_inverted:
            raise ValueError(
                f"New status must be in {list(status_mapping_inverted.keys())}")
        else:
            new_status_str = status_mapping_inverted[new_status]
            new_path = self.path.replace(self.status, new_status_str)
            os.rename(self.path, new_path)
            self.path = new_path
            self._refresh()

    def complete(self):
        self.change_status("done")
        done_dir = os.path.join(self.relative_path, "done")
        if not os.path.exists(done_dir):
            os.mkdir(done_dir)
        new_path = os.path.join(done_dir, self.name)
        os.rename(self.path, new_path)
        self.path = new_path
        self._refresh()

    def rename(self, new_name: str) -> None:
        new_path = self.path.replace(self.name, new_name)
        os.rename(self.path, new_name)
        self.path = new_path
        self._refresh()

    def edit(self) -> None:
        os.system(editor + ' ' + self.path)
        self._refresh()

    def work(self):
        pass

    def prioritize(self):
        pass

    def deprioritize(self):
        pass

    def view(self):
        # Markdown-esque view of file
        pass

    @classmethod
    def new(cls, path):
        with open()



if __name__ == "__main__":
    t = Task("/Users/ardunn/alex/common/projexec/tasks/(priority) [1 - todo] read and think about tri pres.md")
    t = Task("/Users/ardunn/alex/common/projexec/tasks/[1 - todo] look into leighs lstm.md")
    # t = Task("/Users/ardunn/alex/common/projexec/tasks/[adassad] test.md")

    # todo: incorporate these test cases
    # test_cases = ["(priority)", "(asdasda), '[1 - todo]', '[2dasas]', combinations of these]