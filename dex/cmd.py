import os
import shutil

import click
import treelib

from dex.executor import Executor
from dex.util import TerminalStyle
from dex.constants import status_primitives, hold_str, done_str, abandoned_str, ip_str, todo_str

'''
# Top level commands
--------------------
dex init [root path]                                # create a new executor file and save the path somewhere
dex exec                                            # print and start work on the highest importance task, printing all info
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
dex executor view                                   # view weekly schedule
dex executor edit                                   # edit the schedule file


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

dex task [dexid] exec
dex task [dexid] done
dex task [dexid] todo
dex task [dexid] hold
dex task [dexid] aban <<alias for abandon>>
'''

# Constants
PROJECT_SUBCOMMAND_LIST = ["work", "view", "prio", "rename", "rm"]
TASK_SUBCOMMAND_LIST = PROJECT_SUBCOMMAND_LIST + ["edit", "hold", "done"]
CONTAINER_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_ROOT_PATH_LOC = os.path.join(CONTAINER_DIR, "current_root.path")
CURRENT_ROOT_IGNORE_LOC = os.path.join(CONTAINER_DIR, "current_root.ignore")
REFERENCE_PROJSET_PATH = os.path.join(CONTAINER_DIR, "assets/reference_executor")

STATUS_COLORMAP = {"todo": "b", "ip": "y", "hold": "m", "done": "g", "abandoned": "k"}
SUCCESS_COLOR = "c"
ERROR_COLOR = "r"
ts = TerminalStyle()


# Utility functions for getting the current root path
########################################################################################################################
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


def get_current_ignore():
    with open(CURRENT_ROOT_IGNORE_LOC, "r") as f:
        i = f.readlines()
    return [folder.replace("\n", "") for folder in i]


# Utility functions for common CLI tasks
########################################################################################################################
def get_project_header_str(project):
    id_str = ts.f("w", ts.f("u", f"Project {project.id}: {project.name}")) + " ["
    for sp in status_primitives:
        sp_str = "held" if sp == hold_str else sp
        id_str += ts.f(STATUS_COLORMAP[sp], f"{len(project.tasks[sp])} {sp_str}") + ", "
    id_str = id_str[:-2] + "]"
    return id_str


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
    print(ts.f("u", f"Task {task.id}: {task.name}"))
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
        tree.create_node(ts.f(color, sp.capitalize()), sp, parent="header")
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


# Utility functions for checking tasks and projects
########################################################################################################################
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


# Global context level commands ########################################################################################
# dex
@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand != "init":
        checks_root_path_loc()
        e = Executor(path=get_current_root_path(), ignored_dirs=get_current_ignore())
        ctx.obj["EXECUTOR"] = e
        ctx.obj["PMAP"] = e.project_map


# Root level commands ##################################################################################################
# dex init
@cli.command(help="Initialize a new set of projects. You can only have one active.")
@click.argument('path', nargs=1, type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option("--ignore", "-i", multiple=True)
def init(path, ignore):
    if not ignore:
        ignore = tuple()
    descriptor = "existing" if os.path.exists(path) else "new"
    s = Executor(path=path, ignored_dirs=ignore)
    write_path_as_current_root_path(s.path)
    write_ignore(ignore)
    print(f"{descriptor.capitalize()} executor initialized in path: {path}")


# dex work
@cli.command(help="Automatically determine most important task and start work.")
@click.pass_context
def work(ctx):
    e = ctx.obj["EXECUTOR"]
    tasks = e.get_n_highest_priority_tasks(1, include_inactive=False)
    if tasks:
        print_task_work_interface(tasks[0])
    else:
        print(ts.f(ERROR_COLOR, f"No tasks found for any project in executor {e.path}. Add a new task with 'dex task'"))



# @cli.command(help="Get info about your projects.")
# @click.option("--visualize", "-v", is_flag=True, help="Make a graph of current tasks.")
# @click.pass_context
# def info(ctx, visualize):
#     s = ctx.obj["SCHEDULE"]
#     print(f"The current dion working directory is {s.path}")
#     print(f"There are currently {len(s.get_projects())} projects.")
#     print(f"There are currently {len(s.get_n_highest_priority_tasks(n=10000, include_done=False))} active tasks.")
#     print(f"There are currently {len(s.get_n_highest_priority_tasks(n=10000, include_done=True))} total tasks, including done.")
#
#     if visualize:
#         projects = s.get_projects()
#         n_tasks_w_status = {sp: 0 for sp in status_primitives}
#         n_tasks_w_priority = {pp: 0 for pp in priority_primitives}
#         for p in projects:
#             tasks = p.tasks
#             for sp in status_primitives:
#                 n_tasks_w_status[sp] += len(tasks[sp])
#             for pp in priority_primitives:
#                 n_tasks_w_priority[pp] += len([t for t in tasks.all if t.priority == pp and t.status != done_str])
#
#         seaborn.set_style("darkgrid")
#         fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
#         ax_status, ax_prio = axes
#
#         seaborn.barplot([f"priority {pp}" for pp in priority_primitives], [n_tasks_w_priority[pp] for pp in priority_primitives], ax=ax_prio, palette=seaborn.color_palette("Blues_r", len(priority_primitives)))
#         ax_prio.set_title("Current active (not done) tasks by priority")
#         seaborn.barplot(list(status_primitives), [n_tasks_w_status[sp] for sp in status_primitives], ax=ax_status, palette=seaborn.color_palette("Reds_r", len(status_primitives)))
#         ax_status.set_title("All tasks by status")
#
#         fig.tight_layout()
#         plt.show()


# dex example [root path]
# @cli.command(help="Get info about your projects. Enter a new folder path for the project directory!")
# @click.argument("path", type=click.Path(file_okay=False, dir_okay=False))
# def example(path):
#     if os.path.exists(path):
#         print(f"Path {path} exists. Choose a new path.")
#     shutil.copytree(REFERENCE_PROJSET_PATH, path)
#     print(f"New example created at {path}. Use 'dion init {path}' to initialize it and start work!")


# Schedule level commands ##############################################################################################
# dion schedule
@cli.group(invoke_without_command=True, help="Weekly executor (schedule) related commands.")
@click.pass_context
def executor(ctx):
    s = ctx.obj["EXECUTOR"]
    pmap = ctx.obj["PMAP"]
    tree = treelib.Tree()
    tree.create_node(ts.f("u", "Schedule"), "root")
    i = 0
    for day, project_ids in s.schedule.items():
        if project_ids == schedule_all_projects_key:
            valid_pids = list(pmap.keys())
        else:
            valid_pids = project_ids

        is_today = day == datetime.datetime.today().strftime("%A")
        color = "c" if is_today else "w"
        tree.create_node(style.format(color, day), day, data=i, parent="root")
        i += 1

        for j, pid in enumerate(valid_pids):
            project_txt = f"{pmap[pid].name}"
            color = "c" if is_today else "x"
            tree.create_node(style.format(color, project_txt), data=j, parent=day)
    tree.show(key=lambda node: node.data)


# dion schedule edit
@schedule.command(name="edit", help="Edit your weekly schedule via project ids.")
@click.pass_context
def schedule_edit(ctx):
    s = ctx.obj["SCHEDULE"]
    initiate_editor(s.schedule_file)
    print(f"Weekly schedule at {s.schedule_file} written.")


if __name__ == '__main__':
    cli(obj={})
