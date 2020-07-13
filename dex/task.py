import os
import datetime

from dex.constants import dexcode_delimiter_left as ddl, dexcode_delimiter_mid as ddm, dexcode_delimiter_right as ddr, \
    status_primitives_ints as spi, status_primitives_ints_inverted as spi_inverted, effort_primitives, \
    importance_primitives, valid_project_ids, due_date_fmt
from dex.exceptions import DexcodeException


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
    def from_file(cls, path: str):
        with open(path, "r") as f:
            content = f.read()
        dexcode = extract_dexcode_from_content(content)
        dexid, effort, due, importance, status = decode_dexcode(dexcode)
        return cls(dexid, path, effort, due, importance, status)


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


def encode_dexcode(dexid: str, effort: int, due: datetime.datetime, importance: int, status: str) -> str:
    """
    Create a dexcode from python objects which are easy to work with.

    Args:
        dexid (str): The dex ID (single letter followed by a number).
        effort (int): The effort, which must be in the effort_primitives.
        due (datetime.datetime): When the task is due.
        importance (int): The importance, which must be in importance_primitives.
        status (str): The status string, which must be in status_primitives

    Returns:
        dexcode (str): The code representing all metadata about the task which otherwise can't be gathered from the
            file itself.
    """
    if effort not in effort_primitives:
        raise ValueError(f"Effort value '{effort}' not a valid effort primitive: '{effort_primitives}")
    if importance not in importance_primitives:
        raise ValueError(f"Importance value '{importance}' not a valid importance primitive: '{importance_primitives}'")
    if status not in spi_inverted:
        raise ValueError(f"Status string '{status}' not a valid status primitive: '{spi_inverted}'")
    due = due.strftime(due_date_fmt)
    return f"{ddl}{dexid}{ddm}e{effort}{ddm}d{due}{ddm}i{importance}{ddm}s{spi_inverted[status]}{ddr}"


def decode_dexcode(dexcode: str) -> list:
    """
    Decode a dexcode string to python objects which are convenient to work with.

    Args:
        dexcode (str): The dexcode

    Returns:
        parsed_tokens ([str, int, datetime.datetime, int, str]): [dexid, effort, due, importance, status]

    """
    if dexcode.startswith(ddl) and \
            dexcode.endswith(ddr) and \
            dexcode.count(ddm) == 4 and \
            dexcode.count(ddl) == dexcode.count(ddr) == 1:
        tokens = dexcode.replace(ddl, "").replace(ddr, "").split(ddm)
        dexid, effort, due, importance, status = tokens

        parsed_tokens = [dexid]

        for reqchar, code in [("e", effort), ("d", due), ("i", importance), ("s", status)]:
            if not reqchar in code:
                raise ValueError(f"Required token '{reqchar}' not found in '{code}' token string.")

            c = code.replace(reqchar, "")

            if reqchar in ["e", "i", "s"]:
                try:
                    c = int(c)
                except ValueError:
                    raise ValueError(f"Integer value not parsable in token '{code}'")

            if reqchar == "e" and not c in effort_primitives:
                raise ValueError(f"Effort value '{c}' not a valid effort primitive: '{effort_primitives}")
            elif reqchar == "i" and not c in importance_primitives:
                raise ValueError(f"Importance value '{c}' not a valid importance primitive: '{importance_primitives}'")
            elif reqchar == "s":
                if c in spi:
                    c = spi[c]
                else:
                    raise ValueError(f"Status integer '{c}' not a valid status primitive integer: '{spi}")
            elif reqchar == "d":
                try:
                    c = datetime.datetime.strptime(c, due_date_fmt)
                except ValueError:
                    raise ValueError(f"Due date datetime object could not be decoded from '{c}'")
            parsed_tokens.append(c)
        return parsed_tokens
    else:
        raise ValueError(f"Invalid dexcode format: '{dexcode}'")


def extract_dexcode_from_content(content: str) -> str:
    """
    Extract a dexcode from content. The dexcode must be on the first line of the content, and must be preceeded by
    ######dexcode:

    Args:
        content (str): The content in which the dexcode can be found.

    Returns:
        dexcode (str): The dexcode

    """
    id_line = content.split("\n")[0]
    if "######dexcode:" in id_line:
        if all([delim in id_line for delim in (ddr, ddl, ddm)]):
            dexcode = id_line[id_line.find(ddl):id_line.find(ddr) + len(ddr)]
            return dexcode
        else:
            raise ValueError("Content missing required dexcode delimiters")
    else:
        raise ValueError("Content missing required dexcode header on first line.")



if __name__ == "__main__":
    d = datetime.datetime.strptime("2020-07-14", due_date_fmt)

    print(encode_dexcode("a11", 2, d, 1, "done"))

    print(decode_dexcode("{[a11.e2.d2020-07-14.i1.s3]}"))

    with open("/home/dude/dex/dex/example task.md", "r") as f:
        print(extract_dexcode_from_content(f.read()))
