import os
import json

from dionysus.project import Project
from dionysus.constants import schedule_fname, valid_project_ids, default_schedule


class Schedule:
    def __init__(self, path):
        """

        Args:
            path: The path of the root directory containing all projects
        """
        if not os.path.exists(path):
            os.mkdir(path)
        self.path = path

        schedule_file = os.path.join(self.path, schedule_fname)
        if not os.path.exists(schedule_file):
            with open(schedule_file, "w") as f:
                json.dump(default_schedule, f)
            schedule = default_schedule
        else:
            with open(schedule_file, "r") as f:
                schedule = json.load(f)

        self.schedule_file = schedule_file
        self.schedule = schedule

    @property
    def projects(self):
        folders = []
        for folder in os.listdir(self.path):
            full_dirpath = os.path.join(self.path, folder)
            if os.path.isdir(full_dirpath):
                folders.append(full_dirpath)

        projects = []
        for i, folder in enumerate(folders):
            pid = valid_project_ids[i]
            p = Project(folder, pid)
            projects.append(p)
        return projects


if __name__ == "__main__":
    s = Schedule("/home/x/dionysus/dionysus/tmp_projset")
    print(s.projects)
