import os
import shutil
import unittest
from traceback import print_tb
from pathlib import Path

from click.testing import CliRunner

import dion.cmd as dioncli
from dion.constants import schedule_fname, priority_primitives, status_primitives

thisdir = os.path.abspath(os.path.dirname(__file__))
test_projset_path = os.path.join(thisdir, "test_sched")

class SimulatedInput:
    """
    Adapted from https://stackoverflow.com/questions/39506572/how-to-test-function-that-has-two-or-more-inputs-inside
    """
    def __init__(self, *args):
        self.args = iter(args)

    def __call__(self, x):
        try:
            return next(self.args)
        except StopIteration:
            raise Exception("No more input")



class TestTask(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    #
    # @classmethod
    # def tearDownClass(cls) -> None:
    #     shutil.rmtree(edited_filedir)

    def test_new(self):
        # Test init a new project set
        result = self.runner.invoke(dioncli.init, test_projset_path)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(os.path.join(test_projset_path, schedule_fname)))

        # Test making a new project
        for i, syntax in enumerate(["project", "project new"]):
            project_terms = [f"{i}{term}" for term in ["p", "project", "proje-name", "proj1_  82n!@#$%U&*(-=+"]]
            for name in enumerate(project_terms):
                dioncli.input = lambda x: name
                result = self.runner.invoke(dioncli.cli, syntax, obj={})
                self.assertEqual(result.exit_code, 0)
                new_project_path = os.path.join(test_projset_path, name)
                self.assertTrue(os.path.exists(new_project_path))
                self.assertTrue(Path(new_project_path).is_dir)

        # Test making new task
        for i, syntax in enumerate(["task", "task new"]):
            for j, project_id in enumerate(["a", "b"]):
                for k, priority in enumerate(priority_primitives):
                    for l, status in enumerate(status_primitives):
                        task_terms = [f"{i}{j}{k}{l}{term}" for term in ["t", "task", "task-name", "task_ 121 !@#$%^&*()-=_+"]]
                        for j, name in enumerate(task_terms):
                            dioncli.input = SimulatedInput(project_id, name, str(priority), status, "n")
                            result = self.runner.invoke(dioncli.cli, syntax, obj={})
                            self.assertEqual(result.exit_code, 0)


    def test_schedule(self):

    def tearDown(self) -> None:
        dioncli.input = input

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     shutil.rmtree(test_projset_path)


def print_exc_info(result):
    print(result.exit_code)
    tb_tuple = result.exc_info
    print_tb(tb_tuple[-1])
    print(tb_tuple[0])
    print(tb_tuple[1])
    print(result.exception)
    print(result.stdout)

if __name__ == "__main__":
    unittest.main()
