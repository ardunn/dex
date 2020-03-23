# `dion` - a productivity system

#### dion is an ultra-minimal and opinionated productivity system (and CLI tool).
It tells you what to work on and when. You can also create, edit, and view tasks. Use `dion` to get more done in less time with less organization overhead.

![dion](./assets/dionysus.jpg)
###### `dion` is named after the Greek god of fertility and productivity, Dionysus.

# Is `dion` for me?
Take this quiz.

1. Are you tired of trying many "productivity" tools, only to find you spend more time organizing your tasks than you do completing them?
2. Are you worried if you move from Productivity Service #1 to Productivity Service #2 you will lose/have to re-enter all your project and task info?
3. Do you like managing things with simple files (such as markdown) rather than online or app interfaces?
4. Do you find yourself spending too much time figuring out what to work on?
5. Do you like the command line?

If you answered "yes" to 3 or more of these questions, `dion` is for you. Otherwise, move on.


# Highlights
##### View tasks across all projects, ordered intelligently by importance
![dion](./assets/example_tasks.png)

---

##### View tasks by project
![dion](./assets/example_tasks_by_project.png)

---

##### Intelligently and automatically determine what to work on, according to a weekly schedule
![dion](./assets/example_work.png)

---

##### Get an overview
![dion](./assets/example_info.png)
![dion](./assets/example_vis.png)

---

##### Your tasks are markdown files which can be edited however you like (or via `dion` CLI)
![dion](./assets/example_tree.png)


## The System
#### Tasks

Tasks are non-trivial, self-contained units of work. They are individual markdown files. The file name is the name of the task; the contents are whatever you want them to be (notes, subtasks, nothing, etc.).

Tasks have both a *status* (todo, doing, on hold, done) and a priority (1-3, lower is more important).

#### Projects

Projects are long-standing collections of tasks. Projects are folders. Besides containing the task markdown files, the project can contain whatever you want (e.g., dedicated notes folder, code subfolders, etc.). I just have a notes subfolder but it can be whatever you want.

Using these heuristics and your project schedule, `dion` can tell you which tasks (Markdown files) and Projects (folders of tasks) to work on. `dion` works best when you define tasks which require approximately equal time.

#### Schedule

A schedule is your entire set of projects. Your schedule is defined weekly; you can work on one or more projects per day. For example, you work on Projects A and B on MWF, and Project C on Tuesday/Thursday, with Projects D and E on weekends. Your schedule is defined in a single json file in a folder containing your dion project folders.


#### Work

`dion`'s system for choosing work tasks is built on a few core assumptions:

1. Choosing what to work on is hard, especially when you have many projects and tasks.
2. Your time is best spent working on one task (or group of highly related tasks) until it is done, rather than skipping between tasks.
3. Tasks have higher and lower priorities.

Based on your schedule, dion chooses the most important task



# Installation
For now, clone the repo and install via pip:
```bash
$: git clone https://github.com/ardunn/dion
$: pip install ./dion --user
```


Coming soon: PyPi install

### Usage

First, initialize an example to work with:

```bash
$: dion example ~/Downloads/productivity_system  # or your favorite directory
$: dion init ~/Downloads/productivity_system     # creates a new dionysus root.
```

An overview of current projects:

```bash
$: dion projects
```

Projects are groups of tasks. Projects can be something like "Write PhD thesis", or "Create eCommerce site", etc.
Projects in `dion` can be accessed through their *project id*, a single letter.

Now get an overview of tasks for each project.

```bash
$: dion tasks --by-project
```

Tasks are single, non-trivial objectives toward accomplishing your projects. They have a *status* (todo, doing, on hold,
 or done) and a *priority* (1-3, lower is more important).
 
 

Adding a task:
```bash
$: dion task new
```

