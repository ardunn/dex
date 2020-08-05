import os

import click
import treelib

from dex.util import TerminalStyle

'''
# Top level commands
--------------------
dex init [root path]                                # create a new executor file and save the path somewhere
dex work                                            # print and start work on the highest importance task, printing all info
dex info                                            # output some info about the current projects
dex example                                         # create an example directory and set the current project to it

dex tasks                                           # view ordered tasks across projects (default relevant to today, ordered by computed priority)
    Filtering (exclusive) options
    (--by-importance/-i)                            # Tasks ranked strictly by importance
    (--by-effort/-e)                                # Tasks ranked strictly by effort
    (--by-due/-d)                                   # Tasks ranked strictly by due date
    (--by-status/-s)                                # Tasks organized by status, ranked internally by computed priority
    (--by-project/-p)                               # Tasks organized by project, ranked internally by computed priority
    
    Additional options
    (--n-shown/-n [val])                            # limit to this number of total tasks shown
    (--all)                                         # show across all projects, not just today


# Executor commands
-------------------
dex exec view                                       # view weekly schedule
dex exec edit                                       # edit the schedule file


# Project commands
-------------------           
dex project new                                     # make a new project
dex project [id] exec                               # work on this specific project (not recommended)
dex project [id] view                               # show all tasks for this project, ordered by priority             
dex project [id] rename                             # rename a project
dex project [id] rm                                 # delete a project


# Task commands
-------------------
dex task                                            # make a new task
    
dex task [dexid] set ...                            # set an attribute of a task
    (--importance/-i [val]) 
    (--efort/-e [val]) 
    (--due/-d [val) 
    (--status/-s [status])
    (--recurring/-r [days])

dex task [dexid] view                               # view a task
dex task [dexid] edit                               # edit a task
dex task [dexid] rename                             # rename a task


# Task aliases
-------------------
dex task [dexid] imp [val]
dex task [dexid] eff [val]
dex task [dexid] due [val] 
    (--recurring/-r [days])

dex task [dexid] work
dex task [dexid] done
dex task [dexid] todo
dex task [dexid] hold
dex task [dexid] aban <<alias for abandon>>
'''

# Constants
PROJECT_SUBCOMMAND_LIST = ["work", "view", "prio", "rename", "rm"]
TASK_SUBCOMMAND_LIST = PROJECT_SUBCOMMAND_LIST + ["edit", "hold", "done"]
CURRENT_ROOT_PATH_LOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_root.path")
CURRENT_ROOT_IGNORE_LOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_root.ignore")

STATUS_COLORMAP = {"todo": "b", "ip": "y", "hold": "m", "done": "g", "abandoned": "k"}
SUCCESS_COLOR = "c"
ERROR_COLOR = "r"
ts = TerminalStyle()



# Utility functions for getting the current root path
#############################################
def get_current_root_path():
    with open(CURRENT_ROOT_PATH_LOC, "r") as f:
        p = f.read()
    return p


def write_path_as_current_root_path(path: str):
    with open(CURRENT_ROOT_PATH_LOC, "w") as f:
        f.write(path)


def write_ignore(ignore):
    with open(CURRENT_ROOT_IGNORE_LOC, "w") as f:
        for i in ignore:
            f.write(i + "\n")


def checks_root_path_loc():
    if os.path.exists(CURRENT_ROOT_PATH_LOC):
        # print("debug: current root path loc exists!")
        with open(CURRENT_ROOT_PATH_LOC, "r") as f:
            path = f.read()
            if os.path.exists(path):
                # print("debug: current root path exists!")
                return None
    print("No current projects. Use 'dion init' to start your set of projects or move to a new one.")
    click.Context.exit(1)


def get_project_header_str(project):
    id_str = ts.format("w", ts.format("u", f"Project {project.id}: {project.name}")) + " ["
    for sp in status_primitives:
        sp_str = "held" if sp == hold_str else sp
        id_str += ts.format(STATUS_COLORMAP[sp], f"{len(project.tasks[sp])} {sp_str}") + ", "
    id_str = id_str[:-2] + "]"
    return id_str


# Utility functions for printing

def print_projects(pmap, show_n_tasks=3, show_done=False):
    tree = treelib.Tree()
    tree.create_node("All projects", "root")
    i = 0
    for p in pmap.values():
        id_str = get_project_header_str(p)
        tree.create_node(id_str, p.id, parent="root")
        if show_n_tasks:
            ordered_tasks = p.get_n_highest_priority_tasks(n=show_n_tasks, include_done=show_done)
            if ordered_tasks:
                for task in ordered_tasks:
                    task_txt = f"{task.id} ({task.status}) [prio={task.priority}]: {task.name}"
                    tree.create_node(task_txt, i, parent=p.id)
                    i += 1
                if len(p.tasks.all) - len(p.tasks.done) > show_n_tasks:
                    tree.create_node("...", i, parent=p.id)
                    i += 1
            else:
                tree.create_node("No tasks.", i, parent=p.id)
                i += 1
    tree.show(key=lambda node: node.identifier)


def ask_for_yn(prompt, action=None):
    for i in range(3):
        ans = input(f"{prompt} (y/n) ").lower()
        if ans in ("y", "yes"):
            if not isinstance(action, type(None)):
                action()
            return True
        elif ans in ("n", "no"):
            return False
        else:
            print("Please enter `y` or `n`")
    else:
        print(ts.f("r", "No input recieved. Get to work!"))
        click.Context.exit(1)


def print_task_work_interface(task):
    print(ts.format("u", f"Task {task.id}: {task.name}"))
    ask_for_yn("View this task?", action=task.view)
    task.work()
    print(ts.f(SUCCESS_COLOR, f"You're now working on '{task.name}'"))
    print(ts.f("y", "Now get to work!"))


def print_task_collection(project, show_done=False, n_shown=100):
    task_collection = project.tasks
    active_statuses = ["todo", "doing", "hold", "done"]
    if not show_done:
        active_statuses.remove("done")

    id_str = get_project_header_str(project)
    tree = treelib.Tree()
    tree.create_node(id_str, "header")
    nid = 0
    for sp in active_statuses:
        color = STATUS_COLORMAP[sp]
        tree.create_node(ts.format(color, sp.capitalize()), sp, parent="header")
        statused_tasks = task_collection[sp]
        if not statused_tasks:
            nid += 1
            tree.create_node("No tasks.", nid, parent=sp)
            continue
        for i, t in enumerate(statused_tasks):
            nid += 1
            task_txt = f"{t.id} - {t.name} (priority {t.priority})"
            tree.create_node(ts.f(color, task_txt), nid, parent=sp)
            if i >= n_shown:
                break
    tree.show(key=lambda node: node.identifier)


def check_project_id_exists(pmap, project_id):
    if project_id not in pmap.keys():
        print(ts.f(ERROR_COLOR, f"Project ID {project_id} invalid. Select from the following projects:"))
        print_projects(pmap, show_n_tasks=0)
        click.Context.exit(1)


def check_task_id_exists(project, tid):
    if tid not in project.task_map.keys():
        print(ts.f(ERROR_COLOR, f"Task ID {tid} invalid. Select from the following tasks in project '{project.name}':"))
        print_task_collection(project)
        click.Context.exit(1)


def check_input_not_empty(input_str):
    if input_str is None or not input_str.strip():
        print(ts.f(ERROR_COLOR, "Empty or space-only names not allowed."))
        click.Context.exit(1)