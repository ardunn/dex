import os
import json

from dionysus.project import  Project
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
        projects = []
        for i, folder in enumerate([f for f in os.listdir(self.path) if os.path.isdir(f)]):
            pid = valid_project_ids[i]
            p = Project.create_from_spec(pid, self.path, folder, init_notes=True)
            projects.append(p)