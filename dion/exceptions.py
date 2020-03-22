class dionException(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "dion : " + self.msg


class FileTypeError(dionException):
    pass


class FileCharacterError(dionException):
    pass


class FileOverwriteError(dionException):
    pass


class StatusError(dionException):
    pass


class PriorityError(dionException):
    pass


class RootPathError(dionException):
    pass