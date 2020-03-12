import click

'''
# Top level commands
--------------------
dion new [root dir]                   # create a new schedule file and save the path somewhere
dion schedule                         # edit the schedule file
dion work                             # print and start work on the highest importance task, printing pid+tid and all info

dion projects                         # show all projects, ordered by sum of importances of tasks
dion tasks                            # view ordered tasks across all projects


# Project commands
-------------------
dion project [pid] work               # work on a task, only for this project
dion project [pid] view               # view a projects tasks in order of importance
dion project [pid] +prio              # +/- priority of all tasks for a particular project
dion project [pid] rename             # rename a project
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


@click.command()
@click.option('--count', default=1, help='number of greetings')
@click.argument('name')
def hello(count, name):
    for x in range(count):
        click.echo('Hello %s!' % name)


@click.group()
def cli():
    pass


@cli.command()
def initdb():
    click.echo('Initialized the database')


@cli.command()
def dropdb():
    click.echo('Dropped the database')


if __name__ == "__main__":
    # hello()
    cli()
