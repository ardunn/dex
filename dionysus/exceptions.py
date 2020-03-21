class DionysusException(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "dionysus : " + self.msg


class FileTypeError(DionysusException):
    pass


class FileCharacterError(DionysusException):
    pass


class FileOverwriteError(DionysusException):
    pass


class StatusError(DionysusException):
    pass


class PriorityError(DionysusException):
    pass


class RootPathError(DionysusException):
    pass