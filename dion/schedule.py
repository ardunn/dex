import os
import json
import datetime
import itertools

from dion.project import Project
from dion.constants import schedule_fname, valid_project_ids, default_schedule
from dion.logic import order_task_collection
from dion.constants import status_primitives
from dion.util import AttrDict


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

    def get_projects(self):
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

    def get_project_map(self):
        project_map = {}
        for p in self.get_projects():
            project_map[p.id] = p
        return project_map

    def get_n_highest_priority_tasks(self, n=1, include_done=False):
        today = datetime.datetime.today().strftime("%A")
        todays_project_ids = self.schedule[today]
        pmap = self.get_project_map()
        if todays_project_ids == "all":
            todays_project_ids = list(pmap.keys())
        todays_projects = [pmap[pid] for pid in todays_project_ids]
        all_todays_tasks = {}
        for sp in status_primitives:
            all_todays_tasks[sp] = list(itertools.chain(*[p.tasks[sp] for p in todays_projects]))
        all_todays_tasks = AttrDict(all_todays_tasks)
        ordered = order_task_collection(all_todays_tasks, limit=n, include_done=include_done)
        return ordered







if __name__ == "__main__":
    s = Schedule("/home/x/dion/dion/tmp_projset/")
    print(s.work())