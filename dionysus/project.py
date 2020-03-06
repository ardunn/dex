import os

# os.path.abspath("matscholar")

class Project:
    def __init__(self, path):
        self.path = path
        self.name = os.path.dirname(path).split("/")[-1]

    @property
    def tasks(self):
       return os.listdir(self.path)

    def edit(self):
        pass

    def work(self):
        pass

    def prioritize(self):
        pass
