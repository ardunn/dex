import os
import copy
import shutil

import click

from dionysus.schedule import Schedule
from dionysus.project import Project
from dionysus.task import Task
from dionysus.exceptions import RootPathError
from dionysus.util import initiate_editor
from dionysus.constants import valid_project_ids, priority_primitives, status_primitives

'''
# Top level commands
--------------------
dion init [root path]                 # create a new schedule file and save the path somewhere
dion schedule                         # edit the schedule file
dion work                             # print and start work on the highest importance task, printing project_id+tid and all info
dion projects                         # show all projects, ordered by sum of importances of tasks
dion tasks                            # view ordered tasks across all projects


# Project commands
-------------------
dion project work [project_id]               # work on a task, only for this project
dion project view [project_id]               # view a projects tasks in order of importance
dion project prio [project_id]               # +/- priority of all tasks for a particular project
dion project rename [project_id]             # rename a project
dion project new [name]                      # make new project and return project id, then show all project-ids
dion project rm [project_id]                 # delete a project


# Task commands
--------------------
dion task work [task_id]               # work on a specific task
dion task done [task_id]               # mark a task as done
dion task hold [task_id]               # hold a task
dion task rename [task_id]             # rename a task
dion task edit [task_id]               # edit a task
dion task view [task_id]               # view a task
dion task prio [task_id]               # set priorities of task
dion task new                          # create a new task
    ----> asks for task name
    ----> asks for project id
    ----> asks for priority
    ----> asks for status
    ----> asks to edit content, then does it if wanted
'''

CURRENT_ROOT_PATH_LOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_root.path")


def checks_root_path_loc():
    if os.path.exists(CURRENT_ROOT_PATH_LOC):
        # print("debug: current root path loc exists!")
        with open(CURRENT_ROOT_PATH_LOC, "r") as f:
            path = f.read()
            if os.path.exists(path):
                # print("debug: current root path exists!")
                return None
    print("No current project. Use 'dion init' to create a new project.")
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
    n_doing = len(project.tasks.doing)
    n_todo = len(project.tasks.todo)
    n_held = len(project.tasks.hold)
    n_done = len(project.tasks.done)
    id_str = f"ID: {project.id}  |  {project.name} [{n_todo} todo, {n_doing} doing, {n_held} on hold, {n_done} done]"
    return id_str


def print_projects(pmap, show_n_tasks=3, show_done=False):
    for p in pmap.values():
        id_str = get_project_header_str(p)
        print(id_str)
        if show_n_tasks:
            print("-" * len(id_str))
            ordered_tasks = p.get_n_highest_priority_tasks(n=show_n_tasks, include_done=show_done)
            if ordered_tasks:
                for task in ordered_tasks:
                    print(f"\t{task.id} ({task.status}) [prio={task.priority}]: {task.name}")
                if len(p.tasks.all) - len(p.tasks.done) > show_n_tasks:
                    print("\t...")
                print("\n")
            else:
                print("No tasks.\n")


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
        print("No input recieved. Get to work!")
        click.Context.exit(1)


def print_task_work_interface(task):
    print(f"Task {task.id}: {task.name}")
    ask_for_yn("View this task?", action=task.view)
    task.work()
    print(f"You're now working on '{task.name}'")
    print("Now get to work!")


def print_task_collection(task_collection, show_done=False):
    active_statuses = ["todo", "doing", "hold", "done"]
    if show_done:
        active_statuses.remove("done")
    for sp in active_statuses:
        statused_tasks = task_collection[sp]
        sp_str = f"{sp.capitalize()} tasks:"
        print("\t" + sp_str + "\n\t" + "-" * len(sp_str))
        if not statused_tasks:
            print("\t\tNo tasks.\n")
        for t in statused_tasks:
            print(f"\t\t{t.id} - {t.name} (priority {t.priority})\n")


def check_project_id_exists(pmap, project_id):
    if project_id not in pmap.keys():
        print(f"Project ID {project_id} invalid. Select from the following projects:")
        print_projects(pmap, show_n_tasks=0)
        click.Context.exit(1)


def check_task_id_exists(project, tid):
    if tid not in project.task_map.keys():
        print(f"Task ID {tid} invalid. Select from the following tasks in project {project.name}:")
        print_task_collection(project.tasks)
        click.Context.exit(1)


# CLI - level commands

@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    # ctx.obj['CURRENT_ROOT_PATH'] = get_current_root_path()


# Root level commands

# dion init
@cli.command()
@click.argument('path', nargs=1, type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True))
def init(path):
    descriptor = "existing" if os.path.exists(path) else "new"
    s = Schedule(path=path)
    write_path_as_current_root_path(s.path)
    click.echo(f"{descriptor.capitalize()} schedule initialized in path: {path}")


# dion schedule
@cli.command()
def schedule():
    s = Schedule(path=get_current_root_path())
    initiate_editor(s.schedule_file)
    print(f"Weekly schedule at {s.schedule_file} written.")


# dion work
@cli.command()
def work():
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    t = s.get_n_highest_priority_tasks(1)[0]
    print_task_work_interface(t)


# dion projects
@cli.command()
def projects():
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    if s.get_projects():
        print_projects(pmap, show_n_tasks=3)
    else:
        print("No projects. Use 'dion project new' to create a new project.")


# dion tasks
@cli.command()
def tasks():
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    print_projects(pmap, show_n_tasks=100)


# Project level commands--------------------------

# dion project
# @cli.command()
@cli.group(invoke_without_command=False)
@click.argument("project_id", type=click.STRING)
@click.pass_context
def project(ctx, project_id):
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    ctx.obj["SCHEDULE"] = s
    ctx.obj["PMAP"] = pmap
    check_project_id_exists(pmap, project_id)
    ctx.obj["PROJECT"] = pmap[project_id]


# dion project work [project_id]
@project.command(name="work")
# @click.argument("project_id", type=click.STRING)
@click.pass_context
def project_work(ctx):
    p = ctx.obj["PROJECT"]
    t = p.get_n_highest_priority_tasks(n=1)[0]
    print_task_work_interface(t)


# dion project view [project_id]
@project.command(name="view")
@click.argument("project_id", type=click.STRING)
@click.option("--by-status", is_flag=True)
@click.option("--show-done", is_flag=True)
@click.pass_context
def project_view(ctx, project_id, by_status, show_done):
    pmap = ctx.obj["PMAP"]
    check_project_id_exists(pmap, project_id)
    if by_status:
        project = pmap[project_id]
        id_str = get_project_header_str(project)
        print(id_str)
        print_task_collection(project.tasks, show_done=show_done)
    else:
        single_project_pmap = {project_id: pmap[project_id]}
        print_projects(single_project_pmap, show_n_tasks=100, show_done=show_done)


# dion project prio [project_id]
@project.command(name="prio")
@click.argument("project_id", type=click.STRING)
@click.argument("priority", type=click.INT)
@click.pass_context
def project_prio(ctx, project_id, priority):
    pmap = ctx.obj["PMAP"]
    check_project_id_exists(pmap, project_id)
    p = pmap[project_id]
    p.set_task_priorities(priority)
    print(f"Priorities in project '{p.name}' all set to {priority}.")


# dion project rename [project_id]
@project.command(name="rename")
@click.argument("project_id", type=click.STRING)
@click.pass_context
def project_rename(ctx, project_id):
    pmap = ctx.obj["PMAP"]
    check_project_id_exists(project_id)
    p = pmap[project_id]
    old_name = copy.deepcopy(p.name)
    new_name = input("New project name: ")
    p.rename(new_name)
    print(f"Project '{old_name}' renamed to '{p.name}.")


# dion project new
@project.command(name="new")
@click.argument("project_name", type=click.STRING)
@click.option("--no-init-notes", is_flag=True)
@click.pass_context
def project_new(ctx, project_name, no_init_notes):
    current_pids = ctx.obj["PMAP"].keys()
    remaining_pids = copy.deepcopy(valid_project_ids)
    s = ctx.obj["SCHEDULE"]
    for pid in current_pids:
        remaining_pids.remove(pid)
    new_pid = remaining_pids[0]
    print(f"DEBUG: no init notes is {no_init_notes}")
    p = Project.create_from_spec(id=new_pid, path_prefix=s.path, name=project_name, init_notes=not no_init_notes)
    s = Schedule(get_current_root_path())
    print(f"Project `{p.name}` added.")
    print(f"All projects:")
    print_projects(s.get_project_map(), show_n_tasks=0)


@project.command(name="rm")
@click.argument("project_id", type=click.STRING)
@click.pass_context
def project_rm(ctx, project_id):
    pmap = ctx.obj["PMAP"]
    check_project_id_exists(project_id)
    p = pmap[project_id]
    name = copy.deepcopy(p.name)
    shutil.rmtree(p.path)
    print(f"Project {name} removed.")


# Task level commands


def get_task_from_task_id(ctx, task_id):
    pmap = ctx.obj["PMAP"]
    project_id = task_id[0]
    check_project_id_exists(pmap, project_id)
    p = pmap[project_id]
    check_task_id_exists(p, task_id)
    t = p.task_map[task_id]
    return t


# dion task
@cli.group(invoke_without_command=False)
@click.pass_context
def task(ctx):
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    ctx.obj["SCHEDULE"] = s
    ctx.obj["PMAP"] = pmap


# dion task work [task_id]
@task.command(name="work")
@click.argument("task_id", type=click.STRING)
@click.pass_context
def task_work(ctx, task_id):
    t = get_task_from_task_id(ctx, task_id)
    print_task_work_interface(t)


# dion task done [task_id]
@task.command(name="done")
@click.argument("task_id", type=click.STRING)
@click.pass_context
def task_done(ctx, task_id):
    t = get_task_from_task_id(ctx, task_id)
    t.complete()
    print(f"Task {task_id} completed.")


# dion task hold [task_id]
@task.command(name="hold")
@click.argument("task_id", type=click.STRING)
@click.pass_context
def task_hold(ctx, task_id):
    t = get_task_from_task_id(ctx, task_id)
    t.put_on_hold()
    print(f"Task {task_id} completed.")


# dion task rename [task_id]
@task.command(name="rename")
@click.argument("task_id", type=click.STRING)
@click.pass_context
def task_hold(ctx, task_id):
    t = get_task_from_task_id(ctx, task_id)
    old_name = copy.deepcopy(t.name)
    new_name = input("New name: ")
    t.rename(new_name)
    print(f"Task {task_id} renamed from '{old_name}' to '{t.name}'.")


# dion task edit [task_id]
@task.command(name="edit")
@click.argument("task_id", type=click.STRING)
@click.pass_context
def task_edit(ctx, task_id):
    t = get_task_from_task_id(ctx, task_id)
    t.edit()
    print(f"Task {task_id}: '{t.name}' edited.")


# dion task view [task_id]
@task.command(name="view")
@click.argument("task_id", type=click.STRING)
@click.pass_context
def task_view(ctx, task_id):
    t = get_task_from_task_id(ctx, task_id)
    t.view()


# dion task prio [task_id]
@task.command(name="prio")
@click.argument("task_id", type=click.STRING)
@click.argument("priority", type=click.INT)
@click.pass_context
def task_prio(ctx, task_id, priority):
    t = get_task_from_task_id(ctx, task_id)
    if priority not in priority_primitives:
        print(f"Priority is set according to an integer. Priority==1 is most important, priority=={priority_primitives[-1]} least. Select from {priority_primitives}.")
        click.Context.exit(1)
    t.set_priority(priority)
    print(f"Task {task_id}: '{t.name}' priority set to {t.priority}.")


# dion task new
@task.command(name="new")
@click.pass_context
def task_new(ctx):
    pmap = ctx.obj["PMAP"]

    # select project
    header_txt = "Select a project id from the following projects:"
    print(header_txt + "\n" + "-"*len(header_txt))
    print_projects(pmap, show_n_tasks=0)
    project_id = input("Project ID: ")
    check_project_id_exists(pmap, project_id)
    project = pmap[project_id]

    # enter task specifics
    task_name = input("Enter a name for this task: ")
    task_prio = int(input(f"Enter the task's priority ({priority_primitives[0]} - {priority_primitives[-1]}, lower is more important): "))
    task_status = input(f"Enter the task's status (one of {status_primitives}, or hit enter to mark as {status_primitives[0]}: ")
    if not task_status:
        task_status = "todo"
    edit_content = ask_for_yn("Edit the task's content?", action=None)

    # create new task
    t = project.create_new_task(name=task_name, priority=task_prio, status=task_status, edit=edit_content)
    footer_txt = f"Task {t.id}: '{t.name}' created with priority {t.priority} and status '{t.status}'."
    print("\n" + "-"*len(footer_txt) + "\n" + footer_txt)


if __name__ == '__main__':
    cli(obj={})
