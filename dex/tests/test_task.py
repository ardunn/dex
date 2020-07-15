import os
import shutil
import unittest


from dex.task import Task


class TestTask(unittest.TestCase):
    def setUp(self) -> None:
        thisdir = os.path.dirname(os.path.abspath(__file__))
        self.originals_dir = os.path.join(thisdir, "task_files/originals/")
        self.test_dir = os.path.join(thisdir, "task_files/for_tests")
        # if not os.path.exists(self.test_dir)
        # os.mkdir(self.test_dir)
        shutil.copytree(self.originals_dir, self.test_dir)

    def test_task_from_file(self):
        test_flle = os.path.join(self.test_dir, "example task.md")
        t = Task.from_file(test_flle)
        print(t)




if __name__ == "__main__":
    unittest.main()