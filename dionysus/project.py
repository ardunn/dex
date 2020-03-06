import os

# os.path.abspath("matscholar")

class Project:
    def __init__(self, path):
        self.path = path
        self.name = os.path.dirname(path).split("/")[-1]
        self.id = None

    @property
    def tasks(self):
       return os.listdir(self.path)

    def rename(self):
        pass

    def work(self):
        # return high priority tasks
        pass

    def stats(self):
        pass

    def prioritize(self):
        pass

    def deprioritize(self):
        pass

    def list_tasks(self):
        # list tasks and their ids
        pass
