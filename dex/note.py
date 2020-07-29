import os


class Note:
    def __init__(self, path: str):
        self.path = path

    @classmethod
    def from_file(cls, path: str):
        if os.path.exists:
            return cls(path)