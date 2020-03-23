# dion

#### dion is an ultra-minimal and opinionated productivity system (and CLI tool).
It tells you what to work on and when. You can also create, edit, and view tasks. Use `dion` to get more done in less time with less organization overhead.

![dion](./assets/dionysus.jpg)
###### `dion` is named after the Greek god of fertility and productivity, Dionysus.

### Is `dion` for me?
Take this quiz.

1. Are you tired of trying tons of "productivity" tools, only to find you spend more time organizing your tasks than you do completing them?
2. Are you worried if you move from Productivity Service #1 to Productivity Service #2 you will lose all your project and task info?
3. Do you like managing things with simple files (such as markdown) rather than online or app interfaces?
4. Do you find yourself spending too much time figuring out what to work on?
5. Do you like the command line?

If you answered "yes" to 3 or more of these questions, `dion` is for you. Otherwise, move on.


### Demo
```
(cenv) x@kratos [assets]: dion tasks
Top 10 tasks from all 3 projects:
├── c1 (doing) [prio=1]: Look into quantum entanglement
├── b3 (todo) [prio=1]: Commission laser weapon
├── a3 (todo) [prio=1]: Use NLP to scan literature
├── a4 (todo) [prio=2]: Learn biology
├── b2 (todo) [prio=2]: Invent warp drive
├── c3 (todo) [prio=2]: Get liquid nitrogen
├── b1 (doing) [prio=3]: try to make peace
├── a2 (hold) [prio=2]: Create vaccine
└── c2 (hold) [prio=3]: get funding
```


### Tell me more...
`dion` is built on a few core assumptions:

1. Choosing what to work on is hard, especially when you have many projects and tasks.
2. Your time is best spent working on one task (or group of highly related tasks) until it is done, rather than skipping between tasks.
3. Tasks have higher and lower priorities.

Using these heuristics and your project schedule, `dion` can tell you which tasks (Markdown files) and Projects (folders of tasks) to work on. `dion` works best when you define tasks which require approximately equal time.




### Usage




### File format
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

#### `dion` is an interface for working with tasks in this format. 


Instructions and examples to come.
