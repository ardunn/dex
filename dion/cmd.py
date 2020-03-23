import os
import copy
import shutil
import datetime

import click
import treelib

from dion.schedule import Schedule
from dion.project import Project
from dion.util import initiate_editor, Style
from dion.constants import valid_project_ids, priority_primitives, status_primitives, done_str, hold_str, \
    schedule_all_projects_key

'''
# Top level commands
--------------------
dion init [root path]                 # create a new schedule file and save the path somewhere
dion work                             # print and start work on the highest importance task, printing project_id+tid and all info


# Schedule commands
-------------------
dion schedule                          # view weekly schedule
dion schedule edit                     # edit the schedule file


# Project commands
-------------------
dion project                                 # make a new project
dion projects                                # show all projects, ordered by sum of importances of tasks
dion project [project_id] work               # work on a task, only for this project
dion project [project_id] view               # view a projects tasks in order of importance
dion project [project_id] prio               # +/- priority of all tasks for a particular project
dion project [project_id] rename             # rename a project
dion project [project_id] rm                 # delete a project


# Task commands
--------------------
dion task                              # make a new task
dion tasks                             # view ordered tasks across all projects
dion task [task_id] work               # work on a specific task
dion task [task_id] done               # mark a task as done
dion task [task_id] hold               # hold a task
dion task [task_id] rename             # rename a task
dion task [task_id] edit               # edit a task
dion task [task_id] view               # view a task
dion task [task_id] prio               # set priorities of task

'''
PROJECT_SUBCOMMAND_LIST = ["work", "view", "prio", "rename", "rm"]
TASK_SUBCOMMAND_LIST = PROJECT_SUBCOMMAND_LIST + ["edit", "hold", "done"]

CURRENT_ROOT_PATH_LOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_root.path")
PRIORITY_WARNING = f"Invalid integer priority. Priority==1 is most important, priority=={priority_primitives[-1]} least. Select from {priority_primitives}."
STATUS_WARNING = f"Invalid status string. Choose from: {status_primitives}"
style = Style()
status_colormap = {"todo": "b", "doing": "y", "hold": "m", "done": "g"}
SUCCESS_COLOR = "c"
ERROR_COLOR = "r"


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


# @checks_root_path_loc
def get_current_root_path():
    with open(CURRENT_ROOT_PATH_LOC, "r") as f:
        p = f.read()
    return p


def write_path_as_current_root_path(path: str):
    with open(CURRENT_ROOT_PATH_LOC, "w") as f:
        f.write(path)


def get_project_header_str(project):
    id_str = style.format("w", style.format("u", f"Project {project.id}: {project.name}")) + " ["
    for sp in status_primitives:
        sp_str = "held" if sp == hold_str else sp
        id_str += style.format(status_colormap[sp], f"{len(project.tasks[sp])} {sp_str}") + ", "
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
        print(style.format("r", "No input recieved. Get to work!"))
        click.Context.exit(1)


def print_task_work_interface(task):
    print(style.format("u", f"Task {task.id}: {task.name}"))
    ask_for_yn("View this task?", action=task.view)
    task.work()
    print(style.format(SUCCESS_COLOR, f"You're now working on '{task.name}'"))
    print(style.format("y", "Now get to work!"))


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
        color = status_colormap[sp]
        tree.create_node(style.format(color, sp.capitalize()), sp, parent="header")
        statused_tasks = task_collection[sp]
        if not statused_tasks:
            nid += 1
            tree.create_node("No tasks.", nid, parent=sp)
            continue
        for i, t in enumerate(statused_tasks):
            nid += 1
            task_txt = f"{t.id} - {t.name} (priority {t.priority})"
            tree.create_node(style.format(color, task_txt), nid, parent=sp)
            if i >= n_shown:
                break
    tree.show(key=lambda node: node.identifier)


def check_project_id_exists(pmap, project_id):
    if project_id not in pmap.keys():
        print(style.format(ERROR_COLOR, f"Project ID {project_id} invalid. Select from the following projects:"))
        print_projects(pmap, show_n_tasks=0)
        click.Context.exit(1)


def check_task_id_exists(project, tid):
    if tid not in project.task_map.keys():
        print(style.format(ERROR_COLOR, f"Task ID {tid} invalid. Select from the following tasks in project '{project.name}':"))
        print_task_collection(project)
        click.Context.exit(1)


# Global context level commands ########################################################################################
# dion
@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand != "init":
        checks_root_path_loc()
        s = Schedule(path=get_current_root_path())
        pmap = s.get_project_map()
        ctx.obj["SCHEDULE"] = s
        ctx.obj["PMAP"] = pmap


# Root level commands ##################################################################################################
# dion init
@cli.command(help="Initialize a new set of projects. You can only have one active.")
@click.argument('path', nargs=1, type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True))
def init(path):
    descriptor = "existing" if os.path.exists(path) else "new"
    s = Schedule(path=path)
    write_path_as_current_root_path(s.path)
    print(f"{descriptor.capitalize()} schedule initialized in path: {path}")


# dion work
@cli.command(help="Automatically determine most important task and start work.")
@click.pass_context
def work(ctx):
    s = ctx.obj["SCHEDULE"]
    tasks = s.get_n_highest_priority_tasks(1)
    if tasks:
        print_task_work_interface(tasks[0])
    else:
        print(style.format(ERROR_COLOR, f"No tasks found for any project in schedule {s.path}."))


# Schedule level commands ##############################################################################################
# dion schedule
@cli.group(invoke_without_command=True, help="Weekly schedule related commands.")
@click.pass_context
def schedule(ctx):
    s = ctx.obj["SCHEDULE"]
    pmap = ctx.obj["PMAP"]
    tree = treelib.Tree()
    tree.create_node(style.format("u", "Schedule"), "root")
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


# Project level commands ###############################################################################################
# dion projects
@cli.command(help="List all projects.")
@click.pass_context
def projects(ctx):
    s = ctx.obj["SCHEDULE"]
    if s.get_projects():
        print_projects(s.get_project_map(), show_n_tasks=0)
    else:
        print(style.format(ERROR_COLOR, "No projects. Use 'dion project new' to create a new project."))

1
# dion project
# dion project new
@cli.group(invoke_without_command=True, help="Command a single project (do 'dion project' or 'dion project new' w/ no args for new project).")
@click.argument("project_id", nargs=1, type=click.STRING, required=False)
@click.pass_context
def project(ctx, project_id):

    # Avoid scenario where someone types "dion project view" and it interprets "view" as the project id
    if project_id in PROJECT_SUBCOMMAND_LIST:
        print(style.format(ERROR_COLOR, f"To access command '{project_id}' use 'dion project [PROJECT_ID] '{project_id}'."))
        click.Context.exit(1)
    else:
        # new project
        if ctx.invoked_subcommand is None and project_id in [None, "new"]:
            project_name = input("Enter new project name: ")
            current_pids = ctx.obj["PMAP"].keys()
            remaining_pids = copy.deepcopy(valid_project_ids)
            s = ctx.obj["SCHEDULE"]
            for pid in current_pids:
                remaining_pids.remove(pid)
            new_pid = remaining_pids[0]
            p = Project.create_from_spec(id=new_pid, path_prefix=s.path, name=project_name, init_notes=True)
            s = Schedule(get_current_root_path())
            print(f"Project `{p.name}` added.")
            print_projects(s.get_project_map(), show_n_tasks=0)
        else:
            pmap = ctx.obj["PMAP"]
            check_project_id_exists(pmap, project_id)
            ctx.obj["PROJECT"] = pmap[project_id]

            if project_id is not None and ctx.invoked_subcommand is None:
                print("Nothing to do! Invoke a subcommand. Do 'dion project --help' for help.")


# dion project [project_id] work
@project.command(name="work", help="Automatically determine most important task in a project.")
@click.pass_context
def project_work(ctx):
    p = ctx.obj["PROJECT"]
    tasks = p.get_n_highest_priority_tasks(n=1)
    if tasks:
        print_task_work_interface(tasks[0])
    else:
        print(style.format(ERROR_COLOR, f"No tasks found for project {p.id}: '{p.name}'"))


# dion project [project_id] view
@project.command(name="view", help="View all tasks for a single project.")
@click.option("--n-shown", "-n", default=20, help="Number of tasks to show.", type=click.INT)
@click.option("--by-status", is_flag=True, help="Organize tasks by status.")
@click.option("--show-done", is_flag=True, help="Include done tasks in output.")
@click.pass_context
def project_view(ctx, n_shown, by_status, show_done):
    if n_shown is not None:
        n_shown = int(n_shown)
    p = ctx.obj["PROJECT"]
    if by_status:
        print_task_collection(p, show_done=show_done, n_shown=n_shown)
    else:
        print_projects({p.id: p}, show_n_tasks=n_shown, show_done=show_done)


# dion project [project_id] prio
@project.command(name="prio", help="Set all priorities for a project.")
@click.argument("priority", type=click.INT)
@click.pass_context
def project_prio(ctx, priority):
    p = ctx.obj["PROJECT"]
    p.set_task_priorities(priority)
    print(f"Priorities in project '{p.name}' all set to {priority}.")


# dion project [project_id] rename
@project.command(name="rename", help="Rename a project.")
@click.pass_context
def project_rename(ctx):
    p = ctx.obj["PROJECT"]
    old_name = copy.deepcopy(p.name)
    new_name = input("New project name: ")
    p.rename(new_name)
    print(f"Project '{old_name}' renamed to '{p.name}.")


# dion project [project_id] rm
@project.command(name="rm", help="Remove a project and all of its tasks.")
@click.pass_context
def project_rm(ctx):
    p = ctx.obj["PROJECT"]
    name = copy.deepcopy(p.name)
    shutil.rmtree(p.path)
    print(f"Project {name} removed.")


# Task level commands ##################################################################################################

# dion tasks
@cli.command(help="List all (or just some) tasks, ordered by importance.")
@click.option("--n-shown", "-n", help="Number of tasks shown per project. --tasks-only flattens list.", type=click.INT)
@click.option("--by-project", '-p', is_flag=True, help="Organize tasks by project.")
@click.option("--show-done", is_flag=True, help="Include done tasks in output.")
@click.pass_context
def tasks(ctx, n_shown, by_project, show_done):
    if n_shown is not None:
        n_shown = int(n_shown)
    s = ctx.obj["SCHEDULE"]
    pmap = ctx.obj["PMAP"]
    if by_project:
        if n_shown is None:
            n_shown = 3
        print_projects(pmap, show_n_tasks=n_shown)
    else:
        if n_shown is None:
            n_shown = 10
        ordered = s.get_n_highest_priority_tasks(n=n_shown + 1, include_done=show_done)
        append_ellipses = True if len(ordered) > n_shown else False
        ordered = ordered[:n_shown]

        tree = treelib.Tree()
        header_txt = f"Top {n_shown} tasks from all {len(list(ctx.obj['PMAP'].keys()))} projects:"
        tree.create_node(style.format("u", header_txt), "header")
        for i, t in enumerate(ordered):
            if i < 3:
                color = "c"
            elif 8 > i >= 3:
                color = "y"
            else:
                color = "r"
            task_txt = f"{t.id} ({t.status}) [prio={t.priority}]: {t.name}"
            tree.create_node(style.format(color, task_txt), i, parent="header")
        if append_ellipses:
            tree.create_node("...", i + 1, parent="header")
        tree.show(key=lambda node: node.identifier)


# dion task
# dion task new
@cli.group(invoke_without_command=True, help="Commands for a single task (do 'dion task' or 'dion task new' w/ on args for new task).")
@click.argument("task_id", nargs=1, type=click.STRING, required=False)
@click.pass_context
def task(ctx, task_id):

    # Avoid scenario where someone types "dion task view" and it interprets "view" as the project id
    if task_id in TASK_SUBCOMMAND_LIST:
        print(style.format(ERROR_COLOR, f"To access command '{task_id}' use 'dion task [PROJECT_ID] '{task_id}'."))
        click.Context.exit(1)
    else:
        if ctx.invoked_subcommand is None and task_id in [None, "new"]:
            pmap = ctx.obj["PMAP"]

            # select project
            header_txt = "Select a project id from the following projects:"
            print(header_txt + "\n" + "-" * len(header_txt))
            print_projects(pmap, show_n_tasks=0)
            project_id = input("Project ID: ")
            check_project_id_exists(pmap, project_id)
            project = pmap[project_id]

            # enter task specifics
            task_name = input("Enter a name for this task: ")
            task_prio = int(input(
                f"Enter the task's priority ({priority_primitives[0]} - {priority_primitives[-1]}, lower is more important): "))
            if task_prio not in priority_primitives:
                print(PRIORITY_WARNING)
                click.Context.exit(1)
            task_status = input(
                f"Enter the task's status (one of {status_primitives}, or hit enter to mark as {status_primitives[0]}: ")
            if not task_status:
                task_status = "todo"
            if task_status not in status_primitives:
                print(STATUS_WARNING)
                click.Context.exit(1)
            elif task_status == done_str:
                print("You can't make a new task as done. Stop wasting time.")
                click.Context.exit(1)
            edit_content = ask_for_yn("Edit the task's content?", action=None)

            # create new task
            t = project.create_new_task(name=task_name, priority=task_prio, status=task_status, edit=edit_content)
            footer_txt = f"Task {t.id}: '{t.name}' created with priority {t.priority} and status '{t.status}'."
            print("\n" + "-" * len(footer_txt) + "\n" + footer_txt)
        else:
            pmap = ctx.obj["PMAP"]

            try:
                int(task_id[1:])
            except ValueError:
                print(style.format(ERROR_COLOR, f"Task {task_id} not parsed. Task ids are a letter followed by a number. For example, 'a1'."))
                click.Context.exit(1)
            project_id = task_id[0]
            check_project_id_exists(pmap, project_id)
            p = pmap[project_id]
            check_task_id_exists(p, task_id)
            ctx.obj["TASK"] = p.task_map[task_id]
            if task_id is not None and ctx.invoked_subcommand is None:
                print("Nothing to do! Invoke a subcommand. Do 'dion task --help' for help.")


# dion task [task_id] work
@task.command(name="work", help="Work on a single task, manually. [Not recommended]")
@click.pass_context
def task_work(ctx):
    t = ctx.obj["TASK"]
    print_task_work_interface(t)


# dion task [task_id] done
@task.command(name="done", help="Complete a task.")
@click.pass_context
def task_done(ctx):
    t = ctx.obj["TASK"]
    t.complete()
    print(f"Task {t.id}: '{t.name}' completed.")


# dion task [task_id] hold
@task.command(name="hold", help="Put a task on hold (i.e., waiting on someone else).")
@click.pass_context
def task_hold(ctx):
    t = ctx.obj["TASK"]
    t.put_on_hold()
    print(f"Task {t.id}: '{t.name}' held until further notice.")


# dion task [task_id] rename
@task.command(name="rename", help="Rename a task.")
@click.pass_context
def task_hold(ctx):
    t = ctx.obj["TASK"]
    old_name = copy.deepcopy(t.name)
    new_name = input("New name: ")
    t.rename(new_name)
    print(f"Task {t.id} renamed from '{old_name}' to '{t.name}'.")


# dion task [task_id] edit
@task.command(name="edit", help="Edit a task's content.")
@click.pass_context
def task_edit(ctx):
    t = ctx.obj["TASK"]
    t.edit()
    print(f"Task {t.id}: '{t.name}' edited.")


# dion task [task_id] view
@task.command(name="view", help="View a task.")
@click.pass_context
def task_view(ctx):
    t = ctx.obj["TASK"]
    t.view()


# dion task [task_id] prio
@task.command(name="prio", help="Set a task's priority.")
@click.argument("priority", type=click.INT)
@click.pass_context
def task_prio(ctx, priority):
    t = ctx.obj["TASK"]
    if priority not in priority_primitives:
        print(PRIORITY_WARNING)
        click.Context.exit(1)
    t.set_priority(priority)
    print(f"Task {t.id}: '{t.name}' priority set to {t.priority}.")


if __name__ == '__main__':
    cli(obj={})
