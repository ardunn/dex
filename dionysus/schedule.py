import os

from dionysus.task import Task
from dionysus.project import  Project
from dionysus.constants import schedule_fname, valid_project_ids



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
        if not os.path.exists()


    # dion new [root_dir]
    @classmethod
    def create_from_spec(cls, path):
        pass

    @property
    def projects(self):
        projects = []
        for i, folder in enumerate([f for f in os.listdir(self.path) if os.path.isdir(f)]):
            pid = valid_project_ids[i]
            p = Project.create_from_spec(pid, self.path, folder, init_notes=True)
            projects.append(p)