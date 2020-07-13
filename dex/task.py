import os

from dex.constants import dexcode_delimiter_left as ddl, dexcode_delimiter_mid as ddm, dexcode_delimiter_right as ddr, \
    status_primitives_ints as spi, status_primitives_ints_inverted as spi_inverted

class Task:
    def __init__(self, dexid: str, path: str, effort: int, due: int, importance: int, status: int):
        """
        This instantiation means the file on disk must already exist and must match the arguments. After the Task
        has been instantiated,

        """
        self.dexid = dexid
        self.path = path
        self.due = due
        self.effort = effort
        self.importance = importance
        self.status = status

        if not os.path.exists(self.path):
            raise FileNotFoundError("Task was instantiated without corresponding file on disk.")
        elif not self.path.endswith(".md"):
            raise TypeError("Task files must be markdown, and must end in '.md'.")

        relative_path = os.path.dirname(self.path)
        filename_local = os.path.basename(self.path)
        self.name = os.path.splitext(self.path)[0]


    def __str__(self):
        return f"<dion Task {self.dexid} | {self.name} (status={self.status}, due={self.due}, effort={self.effort}, importance={self.importance})"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_file(cls, filename: str):
        pass

    @classmethod
    def from_spec(cls, dexid: str, path: str, effort: int, due: int, importance: int, status: int):
        pass

    def write_state(self):
        pass

#
# def qualifier_converter(to_list, from_list, key) -> Iterable:
#     return to_list[from_list.index(key)]


# def check_priority(priority: int) -> None:
#     if priority not in priority_primitives:
#         raise PriorityError(f"Priority {priority} invalid. Valid priorities are {priority_primitives}")
#
#
# def check_status(status: str) -> None:
#     if status not in status_primitives:
#         raise StatusError(f"Invalid new status {status}. Valid statuses are {status_primitives}")


def encode_dexcode(dexid: str, effort: int, due: int, importance: int, status: str):
    return f"{ddl}{dexid}{ddm}e{effort}{ddm}d{due}{ddm}i{importance}{ddm}s{spi_inverted[status]}{ddr}"

def decode_dexcode(dexcode: str):
    req = (ddl, ddm, ddr)
    if dexcode.startswith(ddl) and dexcode.endswith()
    else:
        raise ValueError(f"Not all required delimiters ({req} found in dexcode '{dexcode}'")






if __name__ == "__main__":

    print(encode_dexcode("a11", 2, 4, 1, "done"))
