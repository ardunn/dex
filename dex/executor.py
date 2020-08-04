import os
import json
import datetime
import itertools
from typing import List, Union

from dex.task import Task
from dex.project import Project
from dex.constants import executor_fname, valid_project_ids, default_executor
from dex.logic import rank_tasks
from dex.constants import status_primitives
from dex.util import AttrDict


class Executor:
    def __init__(self, path, ignored_dirs=None):
        """
        Executor handles all projects and interfaces mostly with the CLI. It is at the top of the hierarchy.

        Args:
            path (str): The path of the root directory containing all projects
            ignored_dirs ([str]): List of directories to ignore in the root executor dir
        """
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.path = path
        self.ignored_dirs = ignored_dirs if ignored_dirs else []

        executor_file = os.path.join(self.path, executor_fname)
        if not os.path.exists(executor_file):
            with open(executor_file, "w") as f:
                json.dump(default_executor, f)
            executor_week = default_executor
        else:
            with open(executor_file, "r") as f:
                executor_week = json.load(f)

        self.executor_file = executor_file
        self.executor_week = executor_week

        folders = []
        for folder in os.listdir(self.path):
            full_dirpath = os.path.join(self.path, folder)
            if os.path.isdir(full_dirpath):
                if folder not in self.ignored_dirs:
                    folders.append(full_dirpath)
        projects = []
        for i, folder in enumerate(folders):
            pid = valid_project_ids[i]
            p = Project.from_files(folder, pid)
            projects.append(p)
        self.projects = projects

    def __str__(self):
        return f"<dex Executor {self.path} | {len(self.projects)} projects>"

    def __repr__(self):
        return self.__str__()

    @property
    def project_map(self) -> dict:
        """
        Mapping of project id to project.

        Returns:
            {str: dex.Project}: Keys are alphabetic character project ids, values are project objects

        """
        return {p.id: p for p in self.projects}

    def get_n_highest_priority_tasks(self, n: int = 1, include_inactive: bool = False) -> List[Task]:
        """
        Get the n highest priority tasks using the executor file (schedule) to determine the valid projects to use.

        Args:
            n (int): Number of tasks to return.
            include_inactive (bool): Include inactive (done+abandoned) tasks in the returned list.

        Returns:

        """
        today = datetime.datetime.today().strftime("%A")
        todays_project_ids = self.executor_week[today]
        pmap = self.project_map
        if todays_project_ids == "all":
            todays_project_ids = list(pmap.keys())
        todays_projects = [pmap[pid] for pid in todays_project_ids]
        all_todays_tasks = {}
        for sp in status_primitives:
            all_todays_tasks[sp] = list(itertools.chain(*[p.tasks[sp] for p in todays_projects]))
        all_todays_tasks = AttrDict(all_todays_tasks)
        ordered = rank_tasks(all_todays_tasks, limit=n, include_inactive=include_inactive)
        return ordered
