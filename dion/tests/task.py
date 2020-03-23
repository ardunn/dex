import os
import shutil
import unittest
from traceback import print_tb

from click.testing import CliRunner

import dion.cmd as dioncli

thisdir = os.path.abspath(os.path.dirname(__file__))
test_schedule_dir = os.path.join(thisdir, "test_sched")


class TestTask(unittest.TestCase):

    # def setUp(self):
    #     self.
    #     pass


    #
    # @classmethod
    # def tearDownClass(cls) -> None:
    #     shutil.rmtree(edited_filedir)

    def test_init(self):
        runner = CliRunner()
        result = runner.invoke(dioncli.init, test_schedule_dir)
        print(result.exit_code)


    def test_new_project(self):
        print("durr")
        runner = CliRunner()
        dioncli.input = lambda x: 'some_input'
        result = runner.invoke(dioncli.cli, "project new", obj={})
        print(result.exit_code)
        tb_tuple = result.exc_info
        print([type(ei) for ei in tb_tuple ])

        print_tb(tb_tuple[-1])
        print(tb_tuple[0])
        print(tb_tuple[1])
        print(result.exception)

        print(result.stdout)



    def tearDown(self) -> None:
        dioncli.input = input


if __name__ == "__main__":
    unittest.main()
