import os
import shutil
import unittest


from dex.project import Project, process_project_id


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
        proj = Project.from_spec(new_projdir)

