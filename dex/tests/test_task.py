import os
import shutil
import unittest
import datetime


from dex.task import Task
from dex.constants import due_date_fmt


class TestTask(unittest.TestCase):
    def setUp(self) -> None:
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.originals_dir = os.path.join(self.this_dir, "task_files/originals/")
        self.test_dir = os.path.join(self.this_dir, "task_files/for_tests")
        shutil.copytree(self.originals_dir, self.test_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    def test_task_from_file(self):
        test_flle = os.path.join(self.test_dir, "example task.md")
        t = Task.from_file(test_flle)
        self.assertEqual(t.dexid, "b44")
        self.assertEqual(t.effort, 2)
        self.assertEqual(t.importance, 5)
        self.assertEqual(t.status, "todo")
        self.assertListEqual(t.flags, ["n"])
        ref_time = datetime.datetime.strptime("2020-07-21", due_date_fmt)
        self.assertTrue( ref_time == t.due)

    def test_task_from_spec(self):
        local_task_file = "task_from_spec task.md"
        test_file = os.path.join(self.test_dir, local_task_file)
        due = datetime.datetime.strptime("2020-08-19", due_date_fmt)
        t = Task.from_spec("a144", test_file, 4, due, 3, "todo", ["r21"])
        self.assertTrue(os.path.exists(test_file))
        self.assertEqual(t.dexid, "a144")
        self.assertEqual(t.effort, 4)
        self.assertEqual(t.importance, 3)
        self.assertEqual(t.status, "todo")
        self.assertListEqual(t.flags, ["r21"])
        ref_time = datetime.datetime.strptime("2020-08-19", due_date_fmt)
        self.assertTrue( ref_time == t.due)




if __name__ == "__main__":
    unittest.main()