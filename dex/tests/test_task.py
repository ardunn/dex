import os
import shutil
import unittest
import datetime


from dex.task import Task
from dex.constants import due_date_fmt, task_extension, todo_str, ip_str, done_str, hold_str, abandoned_str, inactive_subdir


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

    # Testing methods where the state is written to the file
    ########################################################

    def test_rename(self):
        test_flle = os.path.join(self.test_dir, "example task.md")
        t = Task.from_file(test_flle)
        new_name = "renamed file"
        t.rename(new_name)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f"{new_name}{task_extension}")))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, test_flle)))
        self.assertEqual(t.name, new_name)

    def test_set_status(self):
        fname = 'example task.md'
        test_file = os.path.join(self.test_dir, fname)

        # checking setting the same status
        t = Task.from_file(test_file)
        self.assertEqual(t.status, todo_str)
        t.set_status(todo_str)
        t = Task.from_file(test_file)
        self.assertEqual(t.status, todo_str)

        t = Task.from_file(test_file)
        t.set_status(ip_str)
        t = Task.from_file(test_file)
        self.assertEqual(t.status, ip_str)

        t = Task.from_file(test_file)
        t.set_status(hold_str)
        t = Task.from_file(test_file)
        self.assertEqual(t.status, hold_str)

        # moving it into an inactive state from an active state
        t = Task.from_file(test_file)
        t.set_status(done_str)

        expected_newpath = os.path.join(os.path.join(self.test_dir, inactive_subdir), fname)
        self.assertTrue(t.path == expected_newpath)

        # changing the inactive state
        t = Task.from_file(expected_newpath)
        self.assertEqual(t.status, done_str)
        t.set_status(abandoned_str)
        self.assertEqual(t.status, abandoned_str)
        t = Task.from_file(expected_newpath)
        self.assertEqual(t.status, abandoned_str)

        # Changing from inactive to active stae
        t.set_status(todo_str)
        self.assertEqual(t.status, todo_str)
        self.assertEqual(t.path, test_file)
        t = Task.from_file(test_file)
        self.assertEqual(t.status, todo_str)

    def test_setters(self):
        pass

    def test_flag_setting(self):
        pass




if __name__ == "__main__":
    unittest.main()