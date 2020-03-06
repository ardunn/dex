# Dionysus

## This is a work in progress.

#### Dionysus is the Greek god of fertility, fruitfulness, and **productivity.**

#### It is also an ultra-minimal and opinionated productivity tool.

![dionysus](./assets/dionysus.jpg)

It works with task lists in a very specific format:
- Your projects are folders. 
- Your tasks are markdown files in those folders.
- Tasks which are done go in a `done` subfolder.
- Task filenames are prefaced with their statuses.
- Your project schedule is in `<root>/schedule.md`.

Example:
```
/
    schedule.md
    important project/
        done/
        [1 - todo] write some code.md
        [2 - doing] make a commit.md

    get a phd/
        done/
        [1 - todo] write dissertation.md
        (priority) [2 - doing] come up with research ideas.md

    other/
        [1 - todo] send email to someone.md
        [1 - todo] answer jira questions.md

```

#### `dionysus` is an interface for working with tasks in this format. 
It tells you what to work on and when. You can create new tasks or mark existing ones
as doing or done. It can also track the time you spend on each project or task.

Instructions and examples to come.