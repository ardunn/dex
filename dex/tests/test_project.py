import os
import shutil
import unittest


from dex.project import Project, process_project_id


class TestProject(unittest.TestCase):
    def setUp(self) -> None:
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        self.originals_dir = os.path.join(self.this_dir, "project_files/originals/")
        self.test_dir = os.path.join(self.this_dir, "project_fules/for_tests")
        shutil.copytree(self.originals_dir, self.test_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)


    def test_project_from_files(self):
        pass

    def test_project_from_spec(self):
        pass

