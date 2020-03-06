# Dionysus

## This is a work in progress.

#### Dionysus is the Greek god of fertility, fruitfulness, and **productivity.**

#### It is also an ultra-minimal and opinionated productivity tool.
It tells you what to work on and when. You can create new tasks, edit existing one, 
or mark them as doing or done. It can also give stats on how long you've been working on what.
The objective is to get more done in less time without excessive organization or frills. 


![dionysus](./assets/dionysus.jpg)

#### Who is `dionysus` for?
Commmand-line-aholics. People who like to manage their tasks lists as simple
files rather than online interfaces. Pretty much no one else.


#### It works with task lists in a very specific format:
- Your projects are folders. 
- Your tasks are markdown files in a `task` subfolder.
- Your notes for that project are any files in a `notes` subfolder.
- Tasks which are done go in a `done` subfolder.
- Task filenames are prefaced with their statuses.
- Your project schedule is in `<root>/schedule.json`.

Example:
```
/
    schedule.json
    important project/
        notes/
            ...
        tasks/
            done/
            [1 - todo] write some code.md
            [2 - doing] make a commit.md

    get a phd/
        notes/
            ...
        tasks/
            done/
            [1 - todo] write dissertation.md
            (priority) [2 - doing] come up with research ideas.md

    other/
        notes/
            ...
        tasks/
            done/
            [1 - todo] send email to someone.md
            [1 - todo] answer jira questions.md

```

#### `dionysus` is an interface for working with tasks in this format. 


Instructions and examples to come.