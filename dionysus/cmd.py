import os
import copy

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
dion init [root path]                  # create a new schedule file and save the path somewhere
dion schedule                         # edit the schedule file
dion work                             # print and start work on the highest importance task, printing pid+tid and all info

dion projects                         # show all projects, ordered by sum of importances of tasks
dion tasks                            # view ordered tasks across all projects


# Project commands
-------------------
dion project work [pid]               # work on a task, only for this project
dion project view [pid]               # view a projects tasks in order of importance
dion project prio [pid]               # +/- priority of all tasks for a particular project
dion project rename [pid]             # rename a project
dion project new [name]               # make new project and return project id, then show all projec tids


# Task commands
--------------------
dion task [pid+tid] work              # work on a specific task
dion task [pid+tid]s done             # mark a task or tasks as done
dion task [pid+tid] rename            # rename a task
dion task [pid+tid] edit              # edit a task
dion task [pid+tid] view              # view a task
dion task [pid+tid]s prio             # set priorities of tasks
dion task new                         # create a new task
    ----> asks for task name
    ----> asks for project name
    ----> asks for priority
    ----> asks for status
    ----> asks to edit content, then does it if wanted

dion task [pid+tid]s set_status       # manually set status of tasks
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
    click.Context.exit(0)


# @checks_root_path_loc
def get_current_root_path():
    with open(CURRENT_ROOT_PATH_LOC, "r") as f:
        p = f.read()
    return p


def write_path_as_current_root_path(path: str):
    with open(CURRENT_ROOT_PATH_LOC, "w") as f:
        f.write(path)


def print_projects(pmap, show_n_tasks=3):
    for pid, p in pmap.items():
        print(f"ID: {pid}  |  {p.name}")
        if show_n_tasks:
            print("------------------")
            ordered_tasks = p.get_n_highest_priority_tasks(n=show_n_tasks)
            if ordered_tasks:
                for task in ordered_tasks:
                    print(f"\t{task.id}: {task.name}")
                    print("\t...")
                    print("\n")
            else:
                print("No tasks.")



@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    # ctx.obj['CURRENT_ROOT_PATH'] = get_current_root_path()


@cli.command()
@click.argument('path', nargs=1, type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True))
def init(ctx, path):
    descriptor = "existing" if os.path.exists(path) else "new"
    s = Schedule(path=path)
    write_path_as_current_root_path(s.path)
    click.echo(f"{descriptor.capitalize()} schedule initialized in path: {path}")




### Root level commands ###

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
    t = s.get_n_highest_priority_tasks(1)
    print(f"Task {t.id}: {t.name}")
    print("View this task?")

    for i in range(3):
        ans = input("(y/n)").lower()
        if ans in ("y", "yes"):
            t.view()
            break
        elif ans in ("n", "no"):
            break
        else:
            print("Please enter `y` or `n`")
    else:
        print("No input recieved. Get to work!")

    t.work()
    print(f"You're now working on '{t.name}'")
    print("Now get to work!")

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


@cli.command()
@click.pass_context
def tasks(ctx):
    checks_root_path_loc()
    s = Schedule(path=get_current_root_path())
    pmap = s.get_project_map()
    print_projects(pmap, show_n_tasks=100)

### Project level commands ###


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


# dion project view [PID]
@project.command(name="view")
@click.argument("project id", type=click.STRING)
@click.pass_context
def project_view(ctx, pid):
    pmap = ctx.obj["PMAP"]
    if pid not in pmap.keys():
        print(f"Project ID {pid} invalid. Select from the following projects:")
        print_projects(pmap, show_n_tasks=False)


# dion project work [PID]
@project.command(name="work")
@click.argument("project_id", type=click.STRING)
@

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
    Project.create_from_spec(id=new_pid, path_prefix=s.path, name=project_name, init_notes=not no_init_notes)



if __name__ == '__main__':
    cli(obj={})
