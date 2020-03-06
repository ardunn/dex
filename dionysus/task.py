import os
import re

from dionysus.constants import status_regex, priority_regex, priority_keyword, status_mapping, task_extension, lsd, rsd, lpd, rpd


class Task:
    def __init__(self, path):
        self.path = path
        self.relative_path = path.split("/")[-1]
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


    def edit(self):
        pass

    def complete(self):
        pass

    def work(self):
        pass

    def prioritize(self):
        pass


if __name__ == "__main__":
    t = Task("/Users/ardunn/alex/common/projexec/tasks/(priority) [1 - todo] read and think about tri pres.md")
    t = Task("/Users/ardunn/alex/common/projexec/tasks/[1 - todo] look into leighs lstm.md")
    # t = Task("/Users/ardunn/alex/common/projexec/tasks/[adassad] test.md")

    # todo: incorporate these test cases
    # test_cases = ["(priority)", "(asdasda), '[1 - todo]', '[2dasas]', combinations of these]