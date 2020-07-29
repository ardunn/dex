import os
import shutil
import unittest
import datetime


from dex.task import Task, encode_dexcode, decode_dexcode, extract_dexcode_from_content, check_flags_valid
from dex.constants import due_date_fmt, task_extension, todo_str, ip_str, done_str, hold_str, abandoned_str, inactive_subdir, dexcode_header
from dex.exceptions import DexcodeException


class TestTask(unittest.TestCase):
    def setUp(self) -> None:
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.originals_dir = os.path.join(self.this_dir, "task_files/originals/")
        self.test_dir = os.path.join(self.this_dir, "task_files/for_tests")
        shutil.copytree(self.originals_dir, self.test_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    # Encoding tests
    ################

    def test_encoding(self):
        canonical_dexcode = "{[c344.e2.d2098-12-31.i2.s3.fn&r10]}"
        example_time = datetime.datetime.strptime("2098-12-31", due_date_fmt)
        args = ["c344", 2, example_time, 2, "done", ["n", "r10"]]
        encoding = encode_dexcode(*args)
        self.assertEqual(encoding, canonical_dexcode)

        decoding = decode_dexcode(canonical_dexcode)
        self.assertListEqual(decoding[:-1], args[:-1])
        self.assertListEqual(decoding[-1], args[-1])

        content = "SOMEREPEATINGPATTERN"*5 + "\n"
        content = content * 300
        content_plus_dexcode = content + f"\n{dexcode_header}{canonical_dexcode}"
        extracted = extract_dexcode_from_content(content_plus_dexcode)
        self.assertEqual(extracted, canonical_dexcode)
        with self.assertRaises(DexcodeException):
            extract_dexcode_from_content(content)  # no dexcode is included

        self.assertIsNone(check_flags_valid(["n", "r11"]))
        with self.assertRaises(ValueError):
            check_flags_valid(["n", "r11", "q"])

    # Task tests
    ############

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
        self.assertTrue(ref_time == t.due)

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
        test_file = os.path.join(self.test_dir, 'example task.md')
        t = Task.from_file(test_file)
        ny_2099 = datetime.datetime.strptime("2099-01-01", due_date_fmt)
        t.set_due(ny_2099)
        self.assertEqual(ny_2099, t.due)
        t = Task.from_file(test_file)
        self.assertEqual(ny_2099, t.due)

        t.set_importance(1)
        self.assertEqual(t.importance, 1)
        t = Task.from_file(test_file)
        self.assertEqual(t.importance, 1)

        t.set_effort(5)
        self.assertEqual(t.effort, 5)
        t = Task.from_file(test_file)
        self.assertEqual(t.effort, 5)

    def test_flag_setting(self):
        test_file = os.path.join(self.test_dir, 'example task.md')
        t = Task.from_file(test_file)

        test_flag = "r22"
        self.assertTrue("n" in t.flags)
        self.assertTrue(test_flag not in t.flags)
        t.add_flag(test_flag)
        self.assertTrue(test_flag in t.flags)
        t.rm_flag(test_flag)
        self.assertTrue(test_flag not in t.flags)

    # Testing properties
    #####################

    def test_properties(self):
        test_file = os.path.join(self.test_dir, "recurring task.md")
        t = Task.from_file(test_file)
        self.assertListEqual([t.hold, t.done, t.ip, t.todo, t.abandoned], [False, False, True, False, False])
        dtd = (t.due - datetime.datetime.now()).days
        self.assertEqual(dtd, t.days_till_due)

    def test_recurrence(self):
        test_file_recurring = os.path.join(self.test_dir, "recurring task.md")
        t_recurring = Task.from_file(test_file_recurring)

        test_file_nonrecurring = os.path.join(self.test_dir, "example task.md")
        t_nonrecurring = Task.from_file(test_file_nonrecurring)

        recurrence, recurrence_time = t_recurring.recurrence
        self.assertTrue(recurrence)
        self.assertEqual(recurrence_time, 31)

        recurrence, recurrence_time = t_nonrecurring.recurrence
        self.assertFalse(recurrence)
        self.assertIsNone(recurrence_time)

    # Tests dependent on more than 1 method
    #######################################

    def test_setting_recurrence(self):
        test_file = os.path.join(self.test_dir, 'example task.md')
        t = Task.from_file(test_file)
        self.assertEqual((False, None), t.recurrence)
        t.add_flag("r10")
        self.assertEqual((True, 10), t.recurrence)



if __name__ == "__main__":
    unittest.main()