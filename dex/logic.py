import pprint
import random
from typing import List

from dion.util import AttrDict
from dion.task import Task
from dion.constants import priority_primitives


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


def rank_task_list_by_priority(tasks: List[Task]) -> List[Task]:
    """
    Rank a list of tasks based solely on their importance, effort, and due date. Does not factor in the current status
    of the task.

    Args:
        tasks ([Task]): List of tasks, preferrably all with the same status.

    Returns:
        [Task]: A ranked list of the tasks by priority

    """
    prio_tuples = [None] * len(tasks)
    for t in tasks:
        e = t.effort
        i = t.importance
        d = t.due



## name, effort, due, importance, status

tasks = {
    "t1: file stuff for graduation": [1, 2, 5, "todo"],
    "t2: write final project report": [5, 22, 4, "ip"],
    "t3: finish internship application": [1, 14, 4, "ip"],
    "t4: turn in chemistry homework": [2, 8, 3, "ip"],
    "t5: email TA": [1, 11, 1, "todo"]
}



# todo: account for negative due date/overdue tasks
# todo: try normalizing importances and efforts

# higher is higher priority
def priority_score(task):
    e, d, i, s = task

    s_factor = 1.2 if s == "ip" else 1
    p = i ** 2 * s_factor * e/d
    return p



tasks_ranked = []
for task_name, task in tasks.items():
    tasks_ranked.append((task_name, priority_score(task)))

tasks_ranked.sort(key=lambda t: t[1])

pprint.pprint(tasks_ranked)