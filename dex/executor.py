import os
import json
import datetime
import itertools

from dex.project import Project
from dex.constants import executor_fname, valid_project_ids, default_executor
from dex.logic import order_task_collection
from dex.constants import status_primitives
from dex.util import AttrDict


class Executor:
    def __init__(self, path, ignore=None):
        """
        Args:
            path: The path of the root directory containing all projects
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.path = path
        self.ignore = ignore

        executor_file = os.path.join(self.path, executor_fname)
        if not os.path.exists(executor_file):
            with open(executor_file, "w") as f:
                json.dump(default_executor, f)
            executor = default_executor
        else:
            with open(executor_file, "r") as f:
                executor = json.load(f)

        self.executor_file = executor_file
        self.executor = executor

    def get_projects(self):
        folders = []
        for folder in os.listdir(self.path):
            full_dirpath = os.path.join(self.path, folder)
            if os.path.isdir(full_dirpath):
                if folder not in self.ignore:
                    folders.append(full_dirpath)
        projects = []
        for i, folder in enumerate(folders):
            pid = valid_project_ids[i]
            p = Project(folder, pid)
            projects.append(p)
        return projects

    def get_project_map(self):
        project_map = {}
        for p in self.get_projects():
            project_map[p.id] = p
        return project_map

    def get_n_highest_priority_tasks(self, n=1, include_done=False, randomize=False):
        today = datetime.datetime.today().strftime("%A")
        todays_project_ids = self.executor[today]
        pmap = self.get_project_map()
        if todays_project_ids == "all":
            todays_project_ids = list(pmap.keys())
        todays_projects = [pmap[pid] for pid in todays_project_ids]
        all_todays_tasks = {}
        for sp in status_primitives:
            all_todays_tasks[sp] = list(itertools.chain(*[p.tasks[sp] for p in todays_projects]))
        all_todays_tasks = AttrDict(all_todays_tasks)
        ordered = order_task_collection(all_todays_tasks, limit=n, include_done=include_done, randomize=randomize)
        return ordered