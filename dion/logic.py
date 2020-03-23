import random
from typing import List

from dion.util import AttrDict
from dion.task import Task
from dion.constants import priority_primitives


def order_task_collection(task_collection: AttrDict, limit: int = 0, include_done: bool = False, randomize: bool = False) -> List[Task]:
    """

    Order a task collection

    1. deprioritize done
    2. deprioritize hold
    3. priority ordering
    4. doing > todo
    5. ordering based on last edited

    Args:
        task_collection:

    Returns:

    """

    # most important is low index
    if include_done:
        done_ordered = sorted(task_collection.done, key=lambda t: t.priority)
        ordered = done_ordered
    else:
        ordered = []

    hold_ordered = sorted(task_collection.hold, key=lambda t: t.priority)
    ordered = hold_ordered + ordered

    todoing = task_collection.todo + task_collection.doing

    # more advanced ordering for to-do + doing
    todoing_by_priority = {priority: [] for priority in priority_primitives}
    for t in todoing:
        todoing_by_priority[t.priority].append(t)

    # to-doing segregated by priority level, priority levels decreasing
    todoing_by_priority = sorted([(p, tc) for p, tc in todoing_by_priority.items()], key=lambda x: x[0], reverse=True)

    for _, tc in todoing_by_priority:
        # doing has higher priority (lower index) than to-do within a given priority level
        plevel_doing = [t for t in tc if t.doing]
        plevel_todo = [t for t in tc if t.todo]

        if randomize:
            # random order is assigned to otherwise equal tasks
            random.shuffle(plevel_doing)
            random.shuffle(plevel_todo)
        else:
            # oldest modified files are prioritized
            plevel_doing.sort(key=lambda t: t.modification_time)
            plevel_todo.sort(key=lambda t: t.modification_time)

        plevel_ordered = plevel_doing + plevel_todo
        ordered = plevel_ordered + ordered

    if limit:
        return ordered[:limit]
    else:
        return ordered

