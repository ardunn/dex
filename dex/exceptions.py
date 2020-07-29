

class DexException(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "dex : " + self.msg


class DexcodeException(DexException):
    """
    Base class for an exception from a dexcode problem.
    """
    pass


class FileOverwriteError(DexException):
    pass

