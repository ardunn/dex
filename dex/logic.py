import random
from typing import List

from dion.util import AttrDict
from dion.task import Task


def rank_tasks(task_collection: AttrDict, limit: int = 0, include_inactive: bool = False) -> List[Task]:
    """
        Order a task collection

    1. remove abandoned and done tasks
    2. deprioritize held tasks
    3. rank todo and ip tasks by computed priority

    Args:
        task_collection (AttrDict): A collection of Tasks in dict/attr format with keys of status primitives.
        limit (int): Max number of tasks to return 
        include_inactive (bool): If True, includes the inactive (abandoned+done) tasks in the returned list

    Returns:
        [Task]: A list of ranked tasks.
    """

    # most important is low index

    if include_inactive:
        done_ordered = sorted(task_collection.done, key=lambda x: x.priority, reverse=True)
        random.shuffle(task_collection.abandoned)
        ordered = done_ordered + task_collection.abandoned
    else:
        ordered = []

    hold_ordered = sorted(task_collection.hold, key=lambda x: x.priority, reverse=True)
    ordered = hold_ordered + ordered

    todo_and_ip = sorted(task_collection.todo + task_collection.ip, key=lambda x: x.priority, reverse=True)

    ordered = todo_and_ip + ordered

    if limit:
        return ordered[:limit]
    else:
        return ordered