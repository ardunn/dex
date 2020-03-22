import os
import copy
import shutil

import click

from dionysus.schedule import Schedule
from dionysus.project import Project
from dionysus.task import Task
from dionysus.exceptions import RootPathError
from dionysus.util import initiate_editor
from dionysus.constants import valid_project_ids

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


def print_projects(pmap, show_n_tasks=3):
    for p in pmap.values():
        id_str = get_project_header_str(p)
        print(id_str)
        if show_n_tasks:
            print("-" * len(id_str))
            ordered_tasks = p.get_n_highest_priority_tasks(n=show_n_tasks)
            if ordered_tasks:
                for task in ordered_tasks:
                    print(f"\t{task.id}: {task.name}")
                    print("\t...")
                    print("\n")
            else:
                print("No tasks.\n")


def print_task_work_interface(task):
    print(f"Task {task.id}: {task.name}")
    print("View this task?")

    for i in range(3):
        ans = input("(y/n)").lower()
        if ans in ("y", "yes"):
            task.view()
            break
        elif ans in ("n", "no"):
            break
        else:
            print("Please enter `y` or `n`")
    else:
        print("No input recieved. Get to work!")
    task.work()
    print(f"You're now working on '{task.name}'")
    print("Now get to work!")


def print_task_collection(task_collection):
    for sp in ["todo", "doing", "hold", "done"]:
        statused_tasks = task_collection[sp]
        sp_str = f"{sp.capitalize()} tasks:"
        print(sp_str + "\n" + "-" * len(sp_str))
        if not statused_tasks:
            print("No tasks.\n")
        for t in statused_tasks:
            print(f"\t{t.id} - {t.name} (priority {t.priority})\n")


def check_project_id_exists(pmap, project_id):
    if project_id not in pmap.keys():
        print(f"Project ID {project_id} invalid. Select from the following projects:")
        print_projects(pmap, show_n_tasks=0)
        click.Context.exit(1)


def check_task_id_exists(project, tid):
    if tid not in project.tasks.all:
        print(f"Task ID {tid} invalid. Select from the following tasks in project {project.name}:")
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
@cli.command()
@click.argument('path', nargs=1, type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True))
def init(ctx, path):
    descriptor = "existing" if os.path.exists(path) else "new"
    s = Schedule(path=path)
    write_path_as_current_root_path(s.path)
    click.echo(f"{descriptor.capitalize()} schedule initialized in path: {path}")


# dion schedule
@cli.command()
@click.pass_context
def schedule(ctx):
    s = Schedule(path=get_current_root_path())
    initiate_editor(s.schedule_file)
    print(f"Weekly schedule at {s.schedule_file} written.")


# dion work
@cli.command()
@click.pass_context
def work(ctx, path):
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    t = s.get_n_highest_priority_tasks(1)[0]
    print_task_work_interface(t)


# dion projects
@cli.command()
@click.pass_context
def projects(ctx):
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    if s.get_projects():
        print_projects(pmap, show_n_tasks=3)
    else:
        print("No projects. Use 'dion project new' to create a new project.")


# dion tasks
@cli.command()
@click.pass_context
def tasks(ctx):
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    print_projects(pmap, show_n_tasks=100)


# Project level commands--------------------------

# dion project
# @cli.command()
@cli.group(invoke_without_command=False)
@click.pass_context
def project(ctx):
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    ctx.obj["SCHEDULE"] = s
    ctx.obj["PMAP"] = pmap


# dion project work [project_id]
@project.command(name="work")
@click.argument("project_id", type=click.STRING)
@click.pass_context
def project_work(ctx, project_id):
    pmap = ctx.obj["PMAP"]
    check_project_id_exists(pmap, project_id)
    t = pmap[project_id].get_n_highest_priority_tasks(n=1)[0]
    print_task_work_interface(t)


# dion project view [project_id]
@project.command(name="view")
@click.argument("project_id", type=click.STRING)
@click.option("--by-status", is_flag=True)
@click.pass_context
def project_view(ctx, project_id, by_status):
    pmap = ctx.obj["PMAP"]
    check_project_id_exists(pmap, project_id)
    if by_status:
        project = pmap[project_id]
        id_str = get_project_header_str(project)
        print(id_str)
        print_task_collection(project.tasks)
    else:
        single_project_pmap = {project_id: pmap[project_id]}
        print_projects(single_project_pmap, show_n_tasks=100)


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
def task_prio(ctx, task_id):
    t = get_task_from_task_id(ctx, task_id)
    t.set_priority()
    print(f"Task {task_id}: '{t.name}' edited.")



# view prio new


if __name__ == '__main__':
    cli(obj={})
