from dionysus.constants import statuses_pretty, priorities_pretty, task_extension


class DionysusException(BaseException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "dionysus : " + self.msg


class FileTypeError(DionysusException):
    pass


class StatusError(DionysusException):
    pass


class PriorityError(DionysusException):
    pass
