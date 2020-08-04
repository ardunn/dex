import os
import shutil
import unittest
import datetime

from dex.project import Project, process_project_id
from dex.constants import inactive_subdir, tasks_subdir, notes_subdir, due_date_fmt


class TestProject(unittest.TestCase):
    def setUp(self) -> None:
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.originals_dir = os.path.join(self.this_dir, "project_files/originals/")
        self.test_dir = os.path.join(self.this_dir, "project_files/for_tests")
        shutil.copytree(self.originals_dir, self.test_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_project_from_files(self):
        test_projdir = os.path.join(self.test_dir, "project a")
        proj = Project.from_files(test_projdir, "a")
        self.assertEqual(len(proj._tasks), 2)
        self.assertEqual(len(proj._notes), 1)
        self.assertEqual(proj.path, test_projdir)

    def test_project_new(self):
        new_projdir = os.path.join(self.test_dir, "project b")
        proj = Project.new(new_projdir, "q")
        self.assertTrue(os.path.exists(new_projdir))

        notes_dir = os.path.join(new_projdir, notes_subdir)
        self.assertTrue(os.path.exists(notes_dir))

        task_dir = os.path.join(new_projdir, tasks_subdir)
        self.assertTrue(os.path.exists(task_dir))

        inactive_dir = os.path.join(task_dir, inactive_subdir)
        self.assertTrue(os.path.exists(inactive_dir))

        self.assertEqual(proj.tasks_dir, task_dir)
        self.assertEqual(proj.notes_dir, notes_dir)
        self.assertEqual(proj.inactive_dir, inactive_dir)

    def test_rename(self):
        pname = "project a"
        test_projdir = os.path.join(self.test_dir, pname)
        proj = Project.from_files(test_projdir, "a")

        self.assertEqual(proj.name, pname)

        new_project_name = "MDAOSM93838494"
        new_project_path = os.path.join(self.test_dir, new_project_name)
        proj.rename(new_project_name)

        proj = Project.from_files(new_project_path, "a")
        self.assertEqual(proj.name, new_project_name)

    def test_task_behavior(self):
        test_projdir = os.path.join(self.test_dir, "project a")
        proj = Project.from_files(test_projdir, "a")

        # Test adding a new task
        proj.create_new_task(
            "some new task 001 -?",
            1,
            datetime.datetime.strptime("2099-01-01", due_date_fmt),
            3,
            "ip",
            ["r45"],
            edit_content=False
        )

        self.assertEqual(len(proj._tasks), 3)
        self.assertEqual(proj._tasks[-1].dexid, "a402")

        # Test the data structure of the tasks
        self.assertEqual(len(proj._tasks), len(proj.tasks.all))
        self.assertEqual(len(proj.tasks.todo), 1)
        self.assertEqual(proj.tasks.todo[0].dexid, "a401")
        self.assertEqual(len(proj.tasks.ip), 1)
        self.assertEqual(proj.tasks.ip[0].dexid, "a402")
        self.assertEqual(len(proj.tasks.done), 0)
        self.assertEqual(len(proj.tasks.hold), 0)
        self.assertEqual(len(proj.tasks.abandoned), 1)
        self.assertEqual(proj.tasks.abandoned[0].dexid, "a41")

        for dexid, task in proj.task_map.items():
            self.assertEqual(dexid, task.dexid)






