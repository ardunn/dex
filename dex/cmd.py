import os
import copy
import json
import random
import datetime
import shutil

import click
import treelib

from dex.project import Project
from dex.executor import Executor
from dex.logic import rank_tasks
from dex.util import TerminalStyle, initiate_editor
from dex.constants import status_primitives, hold_str, done_str, abandoned_str, ip_str, todo_str, \
    executor_all_projects_key, valid_project_ids, importance_primitives, effort_primitives, max_due_date, due_date_fmt, valid_recurrence_times, recurring_flag, no_flags

'''
# Top level commands
--------------------
dex init [path]                                     # create a new executor file and save the path somewhere
dex exec                                            # print and start work on the highest importance task, printing all info
dex info                                            # output some info about the current projects
dex example [path]                                  # create an example directory


# Executor commands
-------------------
dex executor                                        # view weekly schedule
dex executor edit                                   # edit the schedule file


# Project commands
-------------------
dex projects
dex project new                                     # make a new project
dex project [id]                                    # show all tasks for this project, ordered by priority             
dex project [id] exec                               # work on this specific project (not recommended)
dex project [id] rename                             # rename a project
dex project [id] rm                                 # delete a project


# Task commands
-------------------
dex tasks                                           # view ordered tasks across projects (default relevant to today, ordered by computed priority)
    Filtering (exclusive) options
    (--by-importance/-i)                            # Tasks ranked strictly by importance
    (--by-effort/-e)                                # Tasks ranked strictly by effort
    (--by-due/-d)                                   # Tasks ranked strictly by due date
    (--by-status/-s)                                # Tasks organized by status, ranked internally by computed priority
    (--by-project/-p)                               # Tasks organized by project, ranked internally by computed priority
    
    Additional options
    (--n-shown/-n [val])                            # limit to this number of total tasks shown
    (--all-projects/-a)                             # show across all projects, not just today
    (--include-inactive)                            # show inactive (done+abandoned) tasks
    
dex task                                            # make a new task
dex task [dexid]                                    # view a task
dex task [dexid] edit                               # edit a task
dex task [dexid] rename                             # rename a task
    
dex task [dexid] set ...                            # set an attribute of a task
    (--importance/-i [val]) 
    (--efort/-e [val]) 
    (--due/-d [val) 
    (--status/-s [status])
    (--recurring/-r [days])


# Task aliases (all shorthand for dex task [dexid] set)
-------------------------------------------------------
dex task [dexid] imp [val]                          # set the importance of the task to [val]
dex task [dexid] eff [val]                          # set the effort of the task to [val]
dex task [dexid] due [val]                          # set the due date/recurrence of the task 
    (--recurring/-r [days])

dex task [dexid] exec                               # manually set a task to in progress
dex task [dexid] done                               # complete a task
dex task [dexid] todo                               # mark a task as todo
dex task [dexid] hold                               # put a task on hold
dex task [dexid] aban                               # abandon a task
'''

# Constants
PROJECT_SUBCOMMAND_LIST = ["exec", "rename", "rm"]
TASK_SUBCOMMAND_LIST = PROJECT_SUBCOMMAND_LIST + ["edit", "done", "todo", "hold", "aban", "imp", "eff", "due"]
CONTAINER_DIR = os.path.dirname(os.path.abspath(__file__))
CURRENT_ROOT_PATH_LOC = os.path.join(CONTAINER_DIR, "current_root.path")
CURRENT_ROOT_IGNORE_LOC = os.path.join(CONTAINER_DIR, "current_root.ignore")
MAX_ENTRY_RETRIES = 3

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
    print("No current projects. Use 'dex init' to start your set of projects or move to a new one.")
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


def get_task_string(t, colorize_status=False, id_color="x", name_color="x", attr_color="x", show_details=True):
    recurrence, recurring_n_days = t.recurrence

    if colorize_status:
        status_str = ts.f(STATUS_COLORMAP[t.status], t.status)
    else:
        status_str = t.status
    recurrence_str = f"recurs after {recurring_n_days} days" if recurrence else "non-recurring"
    id_str = ts.f(id_color, f"{t.dexid}")
    name_str = ts.f(name_color, f"{t.name}")
    date_str = t.due.strftime(due_date_fmt)

    dtd = t.days_till_due

    if dtd > 0:
        due_str = f"due in {t.days_till_due} days"
    elif dtd == 0:
        due_str = f"due today"
    else:
        due_str = f"overdue by {abs(t.days_till_due)} days"
    if show_details:
        attr_str = ts.f(attr_color, f"[{due_str} ({date_str}), {t.importance} importance, {t.effort} effort, {recurrence_str}]")
    else:
        attr_str = ""
    return f"{id_str} ({status_str}) - {name_str} {attr_str}"


def print_projects(pmap, show_n_tasks=3, show_inactive=False, **get_task_str_kwargs):
    tree = treelib.Tree()
    tree.create_node("All projects", "root")
    i = 0
    for p in pmap.values():
        id_str = get_project_header_str(p)
        tree.create_node(id_str, p.id, parent="root")
        if show_n_tasks:
            ordered_tasks = rank_tasks(p.tasks, limit=show_n_tasks, include_inactive=show_inactive)
            if ordered_tasks:
                for task in ordered_tasks:
                    task_txt = get_task_string(task, **get_task_str_kwargs)
                    tree.create_node(task_txt, i, parent=p.id)
                    i += 1
                if len(p.tasks.all) - len(p.tasks.done + p.tasks.abandoned) > show_n_tasks:
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
    print(get_task_string(task, colorize_status=True, id_color="u", name_color="u"))
    ask_for_yn("View this task?", action=task.view)
    task.set_status(ip_str)
    print(ts.f(SUCCESS_COLOR, f"You're now working on '{task.name}'"))
    print(ts.f("y", "Now get to work!"))


def print_project_task_collection(project, show_inactive=False, n_shown=10000):
    task_collection = project.tasks
    active_statuses = [todo_str, ip_str, hold_str]
    if show_inactive:
        active_statuses += [abandoned_str, done_str]
    id_str = get_project_header_str(project)
    tree = treelib.Tree()
    tree.create_node(id_str, "header")
    nid = 0
    for sp in active_statuses:
        color = STATUS_COLORMAP[sp]
        sp_str = "In progress" if sp == ip_str else sp.capitalize()
        tree.create_node(ts.f(color, sp_str), sp, parent="header")
        statused_tasks = task_collection[sp]
        if n_shown:
            if not statused_tasks:
                nid += 1
                tree.create_node("No tasks.", nid, parent=sp)
                continue
            for i, t in enumerate(statused_tasks):
                nid += 1
                task_txt = get_task_string(t, colorize_status=True)
                tree.create_node(ts.f(color, task_txt), nid, parent=sp)
                if i >= n_shown:
                    break
    tree.show(key=lambda node: node.identifier)


# Utility functions for checking tasks and projects
########################################################################################################################
def check_project_id_exists(pmap, project_id):
    if project_id not in pmap.keys():
        print(ts.f(ERROR_COLOR, f"Project ID {project_id} invalid. Select from the following projects:"))
        print_projects(pmap, show_n_tasks=0, show_inactive=False)
        click.Context.exit(1)


def check_task_id_exists(project, tid):
    if tid not in project.task_map.keys():
        print(ts.f(ERROR_COLOR, f"Task ID {tid} invalid. Select from the following tasks in project '{project.name}':"))
        print_project_task_collection(project,show_inactive=True)
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
    if ctx.invoked_subcommand not in ["init", "example"]:
        checks_root_path_loc()
        e = Executor(path=get_current_root_path(), ignored_dirs=get_current_ignore())
        ctx.obj["EXECUTOR"] = e
        ctx.obj["PMAP"] = e.project_map


# Root level commands ##################################################################################################
# dex init
@cli.command(help="Initialize a new set of projects. You can only have one active.")
@click.argument('path', nargs=1, type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option("--ignore", "-i", multiple=True, help="Directories to ignore (e.g., ./assets)")
def init(path, ignore):
    if not ignore:
        print(ts.f(ERROR_COLOR,
                   "No ignored directories specified! If any dirs will not be used to hold markdown projects and "
                   "files, please pass them to init one at a time, e.g., 'dex init /path/to/some/folder -i "
                   ".git -i my_special_folder'."))
        print("Creating new executor...")
        ignore = tuple()
    descriptor = "existing" if os.path.exists(path) else "new"
    s = Executor(path=path, ignored_dirs=ignore)
    write_path_as_current_root_path(s.path)
    write_ignore(ignore)
    print(f"{descriptor.capitalize()} executor initialized in path: {path}")


# dex exec
@cli.command(help="Automatically determine most important task and start work.")
@click.pass_context
def exec(ctx):
    e = ctx.obj["EXECUTOR"]
    tasks = e.get_n_highest_priority_tasks(1, include_inactive=False)
    if tasks:
        print_task_work_interface(tasks[0])
    else:
        print(ts.f(ERROR_COLOR, f"No tasks found for any project in executor {e.path}. Add a new task with 'dex task'"))



@cli.command(help="Get info about your projects.")
@click.option("--visualize", "-v", is_flag=True, help="Make a graph of current tasks.")
@click.option("--include-inactive", "-i", is_flag=True, help="Include info on inactive (done and abandoned) tasks.")
@click.pass_context
def info(ctx, visualize, include_inactive):
    import seaborn
    import scipy.stats as spstats
    import matplotlib.pyplot as plt

    e = ctx.obj["EXECUTOR"]
    print(f"The current dex working directory is '{e.path}'")
    print(f"There are currently {len(e.projects)} projects.")

    print(f"There are currently {len(e.get_n_highest_priority_tasks(n=10000, only_today=True, include_inactive=False))} active tasks for today's projects.")
    if include_inactive:
        print(f"There are currently {len(e.get_n_highest_priority_tasks(n=10000, only_today=True, include_inactive=True))} tasks for today's projects, including done and abandoned.")

    print(f"There are currently {len(e.get_n_highest_priority_tasks(n=10000, only_today=False, include_inactive=False))} active tasks for all projects.")
    if include_inactive:
        print(f"There are currently {len(e.get_n_highest_priority_tasks(n=10000, only_today=False, include_inactive=True))} tasks for all projects, including done and abandoned.")

    if visualize:
        std = 3

        primitives = status_primitives if include_inactive else [hold_str, todo_str, ip_str]

        n_tasks_w_status = {sp: 0 for sp in primitives}
        task_density_distributions = []
        for p in e.projects:
            for sp in primitives:
                tasks_w_status = p.tasks[sp]
                n_tasks_w_status[sp] += len(tasks_w_status)
            for t in [task for task in p.tasks.all if task.status in primitives]:
                task_density_distributions.append(spstats.norm(t.days_till_due, std))

        corrective_multiplier = 1/spstats.norm(0, std).pdf(0)

        means = [td.mean() for td in task_density_distributions]
        task_density_domain_positive = list(range(int(max(means)) + std * 5))
        task_density_positive = [sum([td.pdf(day) for td in task_density_distributions]) * corrective_multiplier for day in task_density_domain_positive]

        task_density_domain_negative = list(range(int(min(means)) - std * 5, 1))
        task_density_negative = [sum([td.pdf(day) for td in task_density_distributions]) * corrective_multiplier for day in task_density_domain_negative]


        seaborn.set_style("darkgrid")
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
        ax_status, ax_date = axes

        # seaborn.kdeplot(task_density, shade=True, ax=ax_date)
        # seaborn.relplot(task_density_domain, task_density, ax=ax_date)
        # ax_date.plot([0, 0], [0, max(task_density_positive + task_density_negative)], color="black", linewidth=5)

        ax_date.plot(task_density_domain_positive, task_density_positive, color="blue")
        ax_date.fill_between(task_density_domain_positive, task_density_positive, color="blue", alpha=0.3)

        ax_date.plot(task_density_domain_negative, task_density_negative, color="red")
        ax_date.fill_between(task_density_domain_negative, task_density_negative, color="red", alpha=0.3)

        date_title_str = "All tasks (including done+abandoned)" if include_inactive else "Currently active tasks"
        ax_date.set_title(f"{date_title_str}")
        ax_date.set_xlabel("Days from today")
        ax_date.set_ylabel("Number of tasks")
        seaborn.barplot(list(primitives), [n_tasks_w_status[sp] for sp in primitives], ax=ax_status, palette=seaborn.color_palette("Greens_r", len(primitives)))
        ax_status.set_title("Currently active tasks by status" if not include_inactive else "All tasks (including done+abandoned) by status")
        ax_status.set_ylabel("Number of tasks")

        fig.tight_layout()
        plt.show()


# dex example [root path]
@cli.command(help="Generate an example project in a new folder. Make sure the path to the folder is new (doesn't already exist)")
@click.argument("path", type=click.Path(file_okay=False, dir_okay=False))
def example(path):
    if os.path.exists(path):
        print(ts.f(ERROR_COLOR, f"Path {path} exists. Choose a new path."))
        click.Context.exit(1)
    else:
        projects = {
            "a": "Cure COVID-19",
            "b": "Stop Alien Invasion",
            "c": "Create quantum computer",
            "d": "Write PhD thesis",
            "e": "Build new house"
        }

        for pid, p in projects.items():
            projpath = os.path.abspath(os.path.join(path, p))
            Project.new(projpath, pid)
        e = Executor(path)

        with open(e.executor_file, "w") as f:
            schedule = {
                "Monday": ["a", "c", "e"],
                "Tuesday": ["b", "d"],
                "Wednesday": ["a", "c", "e"],
                "Thursday": ["b", "d"],
                "Friday": ["a", "c", "e"],
                "Saturday": "all",
                "Sunday": "all"
            }
            json.dump(schedule, f)
        e = Executor(path)


        task_names_map = {
            "Cure COVID-19": ["Research literature on vaccines", "Get FDA Approval", "Find adequate host cells", "work out manufacturing contract"],
            "Stop Alien Invasion": ["Begin peace talks with aliens", "Research lazer weaponry", "Activate nuclear missile silos", "Scramble the air force", "Capture specimens for probing weaknesses"],
            "Create quantum computer": ["Develop novel superconductor", "Increase qubit count", "Ask Dr. Hyde about decoherence", "Secure funding from DOE", "Code crypto-cracker"],
            "Write PhD thesis": ["Come up with some new ideas", "Read the literatre", "Schedule qualifying exam", "Email ideas to advisor"],
            "Build new house": ["Call Tyler and sketch floorplan", "Get price quote from auditor", "Negotiate contract with subcontractor", "Pour concrete in basement"],
        }

        time_periods = {
            "overdue": list(range(-20, -1)),
            "within a week": list(range(7)),
            "within a month": list(range(30)),
            "longer": list(range(30, 360)),
            "end": list(range(364))
        }
        for pname, task_names in task_names_map.items():
            for task_name in task_names:
                days_till_due = random.choice(time_periods[random.choice([k for k in time_periods.keys()])])
                date = datetime.datetime.today() + datetime.timedelta(days=days_till_due)
                proj = [p for p in e.projects if p.name == pname][0]
                proj.create_new_task(
                    task_name,
                    random.choice(effort_primitives),
                    date,
                    random.choice(importance_primitives),
                    random.choice([hold_str, todo_str, ip_str]),
                    random.choice([["n"]] * 10 + [["r7"], ["r30"]]),
                    edit_content=False
                )

        mark_as_inactive = e.get_n_highest_priority_tasks(1000, only_today=False, include_inactive=False)
        for i, t in enumerate(random.sample(mark_as_inactive, 4)):
            if i == 3:
                t.set_status(abandoned_str)
            else:
                t.set_status(done_str)
        print(f"New example created at {path}. Use 'dex init {path}' to initialize it and start work!")


# Schedule level commands ##############################################################################################
# dion schedule
@cli.group(invoke_without_command=True, help="Weekly executor (schedule) related commands.")
@click.pass_context
def executor(ctx):
    s = ctx.obj["EXECUTOR"]
    pmap = ctx.obj["PMAP"]
    tree = treelib.Tree()
    tree.create_node(ts.f("u", "Executor Schedule"), "root")
    i = 0
    for day, project_ids in s.executor_week.items():
        if project_ids == executor_all_projects_key:
            valid_pids = list(pmap.keys())
        else:
            valid_pids = project_ids

        is_today = day == datetime.datetime.today().strftime("%A")
        color = "g" if is_today else "w"
        tree.create_node(ts.f(color, day), day, data=i, parent="root")
        i += 1

        if not valid_pids:
            tree.create_node(ts.f("r", "No projects for this day"), data=i, parent=day)
        else:
            for j, pid in enumerate(valid_pids):
                project_txt = f"{pmap[pid].name}"
                color = "g" if is_today else "x"
                tree.create_node(ts.f(color, project_txt), data=j, parent=day)
    tree.show(key=lambda node: node.data)


# dex executor edit
@executor.command(name="edit", help="Edit your weekly schedule via project ids.")
@click.pass_context
def executor_edit(ctx):
    s = ctx.obj["EXECUTOR"]
    initiate_editor(s.executor_file)
    print(f"Weekly schedule at {s.executor_file} written.")


# Project level commands ###############################################################################################
# dex projects
@cli.command(help="List all projects.")
@click.pass_context
def projects(ctx):
    s = ctx.obj["EXECUTOR"]
    if s.projects:
        print_projects(s.project_map, show_n_tasks=0)
    else:
        print(ts.f(ERROR_COLOR, "No projects. Use 'dion project new' to create a new project."))


# dex project
# dex project new
@cli.group(invoke_without_command=True, help="Command a single project \n(do 'dex project new' w/ no args for new project). Do dex project [project_id] to view a project.")
@click.argument("project_id", nargs=1, type=click.STRING, required=False)
@click.pass_context
def project(ctx, project_id):

    # Avoid scenario where someone types "dion project view" and it interprets "view" as the project id
    if project_id in PROJECT_SUBCOMMAND_LIST:
        print(ts.f(ERROR_COLOR, f"To access command '{project_id}' use 'dex project [PROJECT_ID] '{project_id}'."))
        click.Context.exit(1)
    else:
        if ctx.invoked_subcommand is None:
            # new project
            if project_id == "new":
                project_name = input("Enter new project name: ")
                check_input_not_empty(project_name)
                current_pids = ctx.obj["PMAP"].keys()
                remaining_pids = copy.deepcopy(valid_project_ids)
                for pid in current_pids:
                    remaining_pids.remove(pid)
                new_pid = remaining_pids[0]
                e = ctx.obj["EXECUTOR"]
                new_path = os.path.join(e.path, project_name)
                p = Project.new(path=new_path, id=new_pid)
                ignored_dirs = ctx.obj["EXECUTOR"].ignored_dirs
                e = Executor(path=get_current_root_path(), ignored_dirs=ignored_dirs)
                print(f"Project `{p.name}` added.")
                print_projects(e.project_map, show_n_tasks=0)
            else:
                pmap = ctx.obj["PMAP"]
                # view the task
                if project_id is not None:
                    print_project_task_collection(pmap[project_id], show_inactive=True, n_shown=10000)
        else:
            pmap = ctx.obj["PMAP"]
            check_project_id_exists(pmap, project_id)
            ctx.obj["PROJECT"] = pmap[project_id]


# dex project [project_id] exec
@project.command(name="exec", help="Automatically determine most important task in a project.")
@click.pass_context
def project_exec(ctx):
    p = ctx.obj["PROJECT"]
    tasks = rank_tasks(p.tasks)
    if tasks:
        print_task_work_interface(tasks[0])
    else:
        print(ts.f(ERROR_COLOR, f"No tasks found for Project {p.id}: '{p.name}'"))


# dex project [project_id] rename
@project.command(name="rename", help="Rename a project.")
@click.pass_context
def project_rename(ctx):
    p = ctx.obj["PROJECT"]
    old_name = copy.deepcopy(p.name)
    new_name = input("New project name: ")
    check_input_not_empty(new_name)
    p.rename(new_name)
    print(f"Project '{old_name}' renamed to '{new_name}.")


# dex project [project_id] rm
@project.command(name="rm", help="Remove a project and all of its tasks.")
@click.pass_context
def project_rm(ctx):
    p = ctx.obj["PROJECT"]

    name = copy.deepcopy(p.name)

    rm_confirmation = ask_for_yn(f"Really remove project {p}?")
    if rm_confirmation:
        shutil.rmtree(p.path)
        print(f"Project '{name}' removed!")
    else:
        print(f"Project {name} not removed.")


# Task level commands ##################################################################################################
# dex tasks
@cli.command(help="List all (or just some) tasks. By default, organizes by computed priority, and only uses projects for today.")

### Task collection options
@click.option("--n-shown", "-n", help="Number of tasks shown (default is all tasks).", type=click.INT)
@click.option("--all-projects", "-a", is_flag=True, help="Show tasks across all the executor's projects, not just today's.")
@click.option("--include-inactive", "-v", is_flag=True, help="Show done and abandoned tasks.")
@click.option("--hide-task-details", "-h", is_flag=True, help="show task details")
### Ordering options
@click.option("--by-project", '-p', is_flag=True, help="Organize tasks by project. n_shown is shown for each project.")
@click.option("--by-importance", '-i', is_flag=True, help="Organize tasks by importance.")
@click.option("--by-effort", '-e', is_flag=True, help="Organize tasks by effort.")
@click.option("--by-due", '-d', is_flag=True, help="Organize tasks by due date.")
@click.option("--by-status", "-s", is_flag=True, help="Organize tasks by status.")
@click.pass_context
def tasks(ctx, n_shown, all_projects, include_inactive, hide_task_details, by_due, by_status, by_project, by_importance, by_effort):
    orderings = [by_due, by_status, by_project, by_importance, by_effort]
    if sum(orderings) > 1:
        print(ts.f("r", "Please only specify one ordering/organization option (--by-(project/importance/effort/due/status))"))
        click.Context.exit(1)
    show_task_details = not hide_task_details
    if n_shown is None:
        n_shown = 10000
        n_shown_str = "All"
    else:
        n_shown = int(n_shown)
        n_shown_str = f"Top {n_shown}"
    e = ctx.obj["EXECUTOR"]

    only_today = not all_projects
    only_today_str = f"today's projects only" if only_today else "all projects"

    pmap = e.project_map_today if only_today else e.project_map
    tasks_ordered = e.get_n_highest_priority_tasks(n_shown, only_today=only_today, include_inactive=include_inactive)

    tree = treelib.Tree()
    header_txt = f"{n_shown_str} tasks for {only_today_str}"
    if not any(orderings):
        header_txt += " (ordered by computed priority)"
        tree.create_node(ts.f("u", header_txt), "header")
        if tasks_ordered:
            for j, t in enumerate(tasks_ordered):
                if j < 3:
                    color = "r"
                elif 15 > j >= 3:
                    color = "y"
                else:
                    color = "g"

                task_txt = get_task_string(t, colorize_status=True, id_color=color, name_color=color, attr_color="x", show_details=show_task_details)
                # task_txt = ts.f(color, task_txt)
                tree.create_node(task_txt, j, parent="header")
            if len(tasks_ordered) > n_shown:
                tree.create_node("...", j + 1, parent="header")
        else:
            tree.create_node("No tasks", parent="header")
        tree.show(key=lambda node: node.identifier)
    elif by_project:
        print_projects(pmap, show_n_tasks=n_shown, show_inactive=include_inactive, colorize_status=True, show_details = show_task_details)
    elif by_due:

        legend_tree = treelib.Tree()
        legend_tree.create_node("Due date color legend", "header")
        legend_tree.create_node(ts.f("r", "Overdue or due today"), 1, parent="header")
        legend_tree.create_node(ts.f("y", "Due within one week"), 2, parent="header")
        legend_tree.create_node(ts.f("g", "Due within one month"), 3, parent="header")
        legend_tree.create_node(ts.f("b", "Due in 1+ months"), 4, parent="header")
        legend_tree.show(key=lambda node: node.identifier)

        ordered_by_due = sorted(tasks_ordered, key=lambda t: t.days_till_due)
        header_txt += " (ordered by due date)"
        tree.create_node(ts.f("u", header_txt), "header")

        for i, t in enumerate(ordered_by_due):
            dtd = t.days_till_due
            due_date_str = t.due.strftime(due_date_fmt)
            if dtd < 0:
                color = "r"
            elif dtd == 0:
                color = "r"
            elif dtd < 7:
                color = "y"
            elif dtd < 30:
                color = "g"
            else:
                color = "b"
            task_txt = get_task_string(t, colorize_status=False, name_color=color, show_details=show_task_details)
            tree.create_node(task_txt, i, parent="header")
        tree.show(key=lambda node: node.identifier)

    elif by_status:
        tree.create_node(ts.f("u", header_txt + " (ordered by status)"), "header")
        ordered_by_status = {sp: [] for sp in status_primitives}

        # this will already be ordered by computed priortiy
        for task in tasks_ordered:
            ordered_by_status[task.status].append(task)

        node_id = 0
        for sp in [todo_str, ip_str, hold_str, done_str, abandoned_str]:
            task_list = ordered_by_status[sp]
            subheader_id = f"subheader_{sp}"

            sp_str = "In progress" if sp == ip_str else sp.capitalize()
            tree.create_node(ts.f(STATUS_COLORMAP[sp], sp_str), subheader_id, parent="header")
            for i, task in enumerate(task_list):
                node_id += 1
                task_txt = get_task_string(task, colorize_status=False, show_details=show_task_details)
                tree.create_node(task_txt, node_id, parent=subheader_id)
        tree.show(key=lambda node: node.identifier)

    elif by_importance or by_effort:
        # Ordering is the same for both importance and effort
        key = "importance" if by_importance else "effort"
        primitives = importance_primitives if by_importance else effort_primitives

        tree.create_node(ts.f("u", header_txt + f" (ordered by {key})"), "header")
        ordered_by_attr = {p: [] for p in primitives}

        for task in tasks_ordered:
            ordered_by_attr[getattr(task, key)].append(task)

        primitives_colormap = {
            1: "k",
            2: "b",
            3: "g",
            4: "y",
            5: "r"
        }

        node_id = 0
        for p in reversed(primitives):
            color = primitives_colormap[p]
            for task in ordered_by_attr[p]:
                node_id += 1
                task_txt = get_task_string(task, colorize_status=True, id_color=color, name_color=color)
                tree.create_node(task_txt, node_id, parent="header")
        tree.show(key=lambda node: node.identifier)


# dex task
# dex task new
@cli.group(invoke_without_command=True, help="Commands for a single task (do 'dex task new' w/ no args for new task).")
@click.argument("task_id", nargs=1, type=click.STRING, required=False)
@click.pass_context
def task(ctx, task_id):
    pmap = ctx.obj["PMAP"]

    # Avoid scenario where someone types "dion task view" and it interprets "view" as the project id
    if task_id in TASK_SUBCOMMAND_LIST:
        print(ts.f(ERROR_COLOR, f"To access command '{task_id}' use 'dex task [DEX_ID] '{task_id}'."))
        click.Context.exit(1)
    else:
        if ctx.invoked_subcommand is None and task_id == "new":
            # select project
            header_txt = "Select a project id from the following projects:"
            print(header_txt + "\n" + "-" * len(header_txt))
            print_projects(pmap, show_n_tasks=0)
            project_id = input("Project ID: ")
            check_input_not_empty(project_id)
            check_project_id_exists(pmap, project_id)
            project = pmap[project_id]

            # enter task specifics
            task_name = input("Enter a name for this task: ")
            check_input_not_empty(task_name)

            task_due, task_imp, task_eff, task_status, task_flags = None, None, None, None, None

            for _ in range(MAX_ENTRY_RETRIES):
                task_imp = input(
                    f"Enter the task's importance ({importance_primitives[0]} - {importance_primitives[-1]}, higher is more important): ")
                try:
                    task_imp = int(task_imp)
                except ValueError:
                    print(ts.f(ERROR_COLOR, f"Could not convert '{task_imp}' to integer importance. Choose from {importance_primitives}"))
                    continue
                if task_imp not in importance_primitives:
                    print(ts.f(ERROR_COLOR, f"'{task_imp}' is not a valid importance value. Choose from {importance_primitives}"))
                    continue
                else:
                    break
            else:
                print(ts.f(ERROR_COLOR, "Could not parse importance, exiting..."))
                click.Context.exit(1)

            for _ in range(MAX_ENTRY_RETRIES):
                task_eff = input(
                    f"Enter the how much effort the task will take ({effort_primitives[0]} - {effort_primitives[-1]}, higher is more effort): ")
                try:
                    task_eff = int(task_eff)
                except ValueError:
                    print(ts.f(ERROR_COLOR, f"Could not convert '{task_eff}' to integer effort. Choose from {effort_primitives}"))
                    continue
                if task_eff not in effort_primitives:
                    print(ts.f(ERROR_COLOR, f"'{task_eff}' is not a valid effort value. Choose from {effort_primitives}"))
                    continue
                else:
                    break
            else:
                print(ts.f(ERROR_COLOR, "Could not parse effort, exiting..."))
                click.Context.exit(1)

            for _ in range(MAX_ENTRY_RETRIES):
                task_status = input(
                    f"Enter the task's status {status_primitives}, or hit enter to mark as {todo_str}: "
                )
                task_status = todo_str if not task_status else task_status
                if task_status not in status_primitives:
                    print(ts.f(ERROR_COLOR, f"'{task_status}' is not a valid status. Choose from {status_primitives}"))
                    continue
                elif task_status == done_str:
                    print(ts.f(ERROR_COLOR, "You can't make a new task as done. Stop wasting time."))
                    click.Context.exit(1)
                else:
                    break
            else:
                print(ts.f(ERROR_COLOR, "Could not parse status, exiting..."))
                click.Context.exit(1)

            for _ in range(MAX_ENTRY_RETRIES):
                task_due = input(
                    f"Enter the task's due date, (YYYY-MM-DD date or # days due from today) \n(press enter for the max due date, 365 days from now): "
                )
                if not task_due:
                    task_due = max_due_date
                    break
                else:
                    try:
                        task_due_int = int(task_due)
                        task_due = datetime.datetime.today() + datetime.timedelta(days=task_due_int)
                        break
                    except ValueError:
                        try:
                            task_due = datetime.datetime.strptime(task_due, due_date_fmt)
                            break
                        except ValueError:
                            print(ts.f(ERROR_COLOR, f"The entry '{task_due}' could not be parsed as a date or number of days."))
                            continue
            else:
                print(ts.f(ERROR_COLOR, "Could not parse due date, exiting..."))
                click.Context.exit(1)

            if ask_for_yn("Is the task recurring?"):
                for _ in range(MAX_ENTRY_RETRIES):
                    n_days_recurring = input(
                        "Enter the number of days after the due date that this task should recur: "
                    )
                    try:
                        n_days_recurring = int(n_days_recurring)
                    except ValueError:
                        print(ts.f(ERROR_COLOR,
                            f"Could not convert '{n_days_recurring}' to integer days recurring. Choose a number of days between {valid_recurrence_times[0]} - {valid_recurrence_times[-1]}"))
                        break
                    if n_days_recurring not in valid_recurrence_times:
                        print(ts.f(ERROR_COLOR,
                                   f"'{n_days_recurring}' is not a valid recurrence interval. Choose a number of days between {valid_recurrence_times[0]} - {valid_recurrence_times[-1]}"))
                        continue
                    else:
                        task_flags = [f"r{n_days_recurring}"]
                        break
            else:
                task_flags = ["n"]

            edit_content = ask_for_yn("Edit the task's content?", action=None)
            # create new task
            t = project.create_new_task(task_name, task_eff, task_due, task_imp, task_status, task_flags, edit_content)
            footer_txt = f"Task created: {get_task_string(t)}"
            print("\n" + "-" * len(footer_txt) + "\n" + footer_txt)

        elif ctx.invoked_subcommand is None and task_id is None:
            click.echo(ctx.get_help())
            click.Context.exit(0)
        else:
            try:
                int(task_id[1:])
            except ValueError:
                print(ts.f(ERROR_COLOR, f"Task {task_id} not parsed. Task ids are a letter followed by a number. For example, 'a1'."))
                click.Context.exit(1)
            project_id = task_id[0]
            check_project_id_exists(pmap, project_id)
            p = pmap[project_id]
            check_task_id_exists(p, task_id)
            t= p.task_map[task_id]
            ctx.obj["TASK"] = t

            # dex task [dexid] (view it)
            if task_id is not None and ctx.invoked_subcommand is None:
                print(get_task_string(t, colorize_status=True), "\n")
                print(t.view())

# dex task [dexid] edit
@task.command(name="edit", help="Edit a task's content.")
@click.pass_context
def task_edit(ctx):
    t = ctx.obj["TASK"]
    t.edit()
    print(f"Task {t.dexid}: '{t.name}' edited.")


# dex task [dexid] rename
@task.command(name="rename", help="Rename a task.")
@click.pass_context
def task_rename(ctx):
    t = ctx.obj["TASK"]
    old_name = copy.deepcopy(t.name)
    print(f"Old name: {old_name}")
    new_name = input("New name: ")
    check_input_not_empty(new_name)
    t.rename(new_name)
    print(f"Task {t.dexid} renamed from '{old_name}' to '{t.name}'.")


# dex task [dexid] set [args]
@task.command(name="set", help="Change a task's importance, effort, status, and/or due date and recurrence.")
@click.option("--importance", "-i", help=f"Set a task's importance {importance_primitives}", type=click.INT)
@click.option("--effort", "-e", help=f"Set a task's effort {effort_primitives}", type=click.INT)
@click.option("--status", "-s", help=f"Set a task's status {status_primitives}", type=click.STRING)
@click.option("--due", "-d", help=f"Set a task's due date (YYYY-MM-DD or # days until due")
@click.option("--recurring", "-r", help="Change or enable task recurrence (1-365 day intervals). Enter the number of days until it recurs (0 to make the task not recurring)", type=click.INT)
@click.pass_context
def task_set(ctx, importance, effort, status, due, recurring):
    _task_set(ctx, importance, effort, status, due, recurring)


def _task_set(ctx, importance, effort, status, due, recurring):
    has_error = False
    if importance is not None and int(importance) not in importance_primitives:
        print(ts.f(ERROR_COLOR, f"{importance} not a valid importance value {importance_primitives}"))
        has_error = True
    if effort is not None and int(effort) not in effort_primitives:
        print(ts.f(ERROR_COLOR, f"{effort} not a valid effort value {effort_primitives}"))
        has_error = True
    if status is not None and status not in status_primitives:
        print(ts.f(ERROR_COLOR, f"{status} not a valid status {status_primitives}"))
        has_error = True

    task_due = None
    if due is not None:
        try:
            task_due_int = int(due)
            task_due = datetime.datetime.today() + datetime.timedelta(days=task_due_int)
        except ValueError:
            try:
                task_due = datetime.datetime.strptime(due, due_date_fmt)
            except ValueError:
                print(ts.f(ERROR_COLOR, f"The entry '{due}' could not be parsed as a date or number of days."))
                has_error = True

    if recurring is not None:
        recurring = int(recurring)
        if recurring not in valid_recurrence_times and recurring != 0:
            print(ts.f(ERROR_COLOR, f"{recurring} not a valid recurrence time."))
            has_error = True

    if has_error:
        print(ts.f(ERROR_COLOR, f"Errors encountered during argument parsing. Task not updated. See `dex task [dexid] set for more information."))
        click.Context.exit(1)
    else:
        t = ctx.obj["TASK"]
        if importance is not None:
            t.set_importance(importance)
        if effort is not None:
            t.set_effort(effort)
        if due is not None:
            t.set_due(task_due)
        if status is not None:
            print(f"Changing status to {status}")
            t.set_status(status)
        if recurring is not None:
            recurring_flags = [f for f in t.flags if recurring_flag in f]
            for f in recurring_flags:
                t.rm_flag(f)

            # if r is 0, all the recurrences have been removed, so only do stuff if r != 0
            if recurring == 0 and no_flags not in t.flags:
                t.add_flag(no_flags)
            if recurring != 0:
                t.add_flag(f"r{recurring}")
        success_text = ts.f(SUCCESS_COLOR, f"Task {t.dexid} successfully updated to:")
        print(f"{success_text}\n{get_task_string(t)}\n")


# dex task [dexid] done
@task.command(name="done", help="Mark a task as done. Shorthand for the 'set' subcommand")
@click.pass_context
def task_done(ctx):
    _task_set(ctx, None, None, done_str, None, None)

# dex task [dexid] exec
@task.command(name="exec", help="Force work on this task (change status to in progress). Shorthand for the 'set' subcommand. See 'dex task set' for more info on valid arguments.")
@click.pass_context
def task_exec(ctx):
    _task_set(ctx, None, None, ip_str, None, None)


# dex task [dexid] todo
@task.command(name="todo", help="Mark a task as todo. Shorthand for the 'set' subcommand. See 'dex task set' for more info on valid arguments.")
@click.pass_context
def task_todo(ctx):
    _task_set(ctx, None, None, todo_str, None, None)


# dex task [dexid] aban
@task.command(name="aban", help="Mark a task as abandoned. Shorthand for the 'set' subcommand. See 'dex task set' for more info on valid arguments.")
@click.pass_context
def task_aban(ctx):
    _task_set(ctx, None, None, abandoned_str, None, None)


# dex task [dexid] hold
@task.command(name="hold", help="Hold a task (keep active but suspend till further notice). Shorthand for the 'set' subcommand. See 'dex task set' for more info on valid arguments.")
@click.pass_context
def task_hold(ctx):
    _task_set(ctx, None, None, hold_str, None, None)


# dex task [dexid] imp [val]
@task.command(name="imp", help="Change a task's importance. Shorthand for the 'set' subcommand. See 'dex task set' for more info on valid arguments.")
@click.argument("importance", nargs=1, type=click.INT)
@click.pass_context
def task_imp(ctx, importance):
    _task_set(ctx, importance, None, None, None, None)


# dex task [dexid] eff [val]
@task.command(name="eff", help="Change a task's effort. Shorthand for the 'set' subcommand. See 'dex task set' for more info on valid arguments.")
@click.argument("effort", nargs=1, type=click.INT)
@click.pass_context
def task_eff(ctx, effort):
    _task_set(ctx, None, effort, None, None, None)


# dex task [dexid] due [val]
@task.command(name="due", help="Change a task's due date. Shorthand for the 'set' subcommand. See 'dex task set' for more info on valid arguments.")
@click.argument("due", nargs=1)
@click.option("--recurring", "-r", help="Change or enable task recurrence (1-365 day intervals). Enter the number of days until it recurs (0 to make the task not recurring)", type=click.INT)
@click.pass_context
def task_due(ctx, due, recurring):
    _task_set(ctx, None, None, None, due, recurring)


if __name__ == '__main__':
    cli(obj={})