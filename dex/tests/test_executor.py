import os
import json
import shutil
import unittest
import datetime

from dex.executor import Executor
from dex.constants import executor_fname, default_executor


class TestExecutor(unittest.TestCase):
    def setUp(self) -> None:
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.originals_dir = os.path.join(self.this_dir, "executor_files/originals/")
        self.test_dir = os.path.join(self.this_dir, "executor_files/for_tests")
        shutil.copytree(self.originals_dir, self.test_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_executor_construction(self):
        executor = Executor(self.test_dir, ignored_dirs=["ignored_directory"])
        self.assertEqual(len(executor.projects), 2)
        self.assertListEqual(list(executor.project_map.keys()), ["a", "b"])

        # Ensure default schedule is written if it does not exist
        def_ex = os.path.abspath(os.path.join(self.test_dir, executor_fname))
        self.assertTrue(os.path.exists(def_ex))
        self.assertEqual(def_ex, executor.executor_file)

        with open(def_ex, "r") as f:
            def_ex_week = json.load(f)
        self.assertDictEqual(def_ex_week, default_executor)

    def test_task_prios(self):
        executor = Executor(self.test_dir, ignored_dirs=["ignored_directory"])
        tasks = executor.get_n_highest_priority_tasks(100)
        self.assertEqual(len(tasks), 2)
        tasks = executor.get_n_highest_priority_tasks(100, include_inactive=True)
        self.assertEqual(len(tasks), 4)




