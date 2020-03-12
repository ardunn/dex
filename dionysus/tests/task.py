import os
import shutil
import unittest

from dionysus.task import Task

thisdir = os.path.abspath(os.path.dirname(__file__))
original_filedir = os.path.join(thisdir, "task/good/original")
edited_filedir = os.path.join(thisdir, "task/good/edited")


class TestTask(unittest.TestCase):

    # def setUp(self):
    #     self.
    #     pass

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.exists(edited_filedir):
            shutil.rmtree(edited_filedir)
        shutil.copytree(original_filedir, edited_filedir)

    def test_initialize(self):
        for fp in os.listdir(edited_filedir):
            full_path = os.path.join(edited_filedir, fp)
            print("-------")
            print(full_path)
            print("-------")
            t = Task(full_path, 0)
            print(t.status)
            print(t.name)
            print(t.prefix_path)
            print(t.id)
            print(t.priority)
            print(t.content)
            t.view()
            print("\n\n\n")

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(edited_filedir)


if __name__ == "__main__":
    unittest.main()
