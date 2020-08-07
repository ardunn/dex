import os
import json
import itertools
from typing import List, Union, Iterable

from dex.task import Task
from dex.project import Project
from dex.constants import executor_fname, valid_project_ids, default_executor, executor_all_projects_key
from dex.constants import today_in_executor_format as today
from dex.logic import rank_tasks
from dex.constants import status_primitives
from dex.util import AttrDict


class Executor:
    def __init__(self, path: str, ignored_dirs: Union[Iterable, None] = None):
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

    @property
    def project_map_today(self):
        """
        Get the project id : project obj map, but only for today's projects.

        Returns:
            {str: dex.Project}: Keys are alphabetic character project ids, values are project objects
        """
        todays_project_ids = self.executor_week[today]
        pmap = self.project_map
        if todays_project_ids == executor_all_projects_key:
            todays_project_ids = list(pmap.keys())
        return {p.id: p for p in self.projects if p.id in todays_project_ids}

    def get_tasks(self, only_today: bool) -> AttrDict:
        """
        Get a task collection of tasks across more than one project.

        Args:
            only_today (bool): If True, include only the projects which are specified for today.

        Returns:
            AttrDict: The task collection across

        """

        pmap = self.project_map_today if only_today else self.project_map
        relevant_tasks = {}
        for sp in status_primitives:
            relevant_tasks[sp] = list(itertools.chain(*[p.tasks[sp] for p in pmap.values()]))
        relevant_tasks = AttrDict(relevant_tasks)
        return relevant_tasks

    def get_n_highest_priority_tasks(self, n: int = 1, only_today: bool = False, include_inactive: bool = False) -> List[Task]:
        """
        Get the n highest priority tasks using the executor file (schedule) to determine the valid projects to use.

        Args:
            n (int): Number of tasks to return.
            include_inactive (bool): Include inactive (done+abandoned) tasks in the returned list.
            only_today (bool): If True, include only the projects which are specified for today.

        Returns:
            [Task]: List of ordered tasks

        """
        all_todays_tasks = self.get_tasks(only_today=only_today)
        ordered = rank_tasks(all_todays_tasks, limit=n, include_inactive=include_inactive)
        return ordered
