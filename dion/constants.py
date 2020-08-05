import os
import string

import mdv

mdv.term_columns = 60

lpd = "{"
rpd = "}"
priority_primitives = tuple(range(1, 4)) #0 means on hold, then 1=most important, 3=least important
priorities_pretty = tuple([f"{lpd}{priority}{rpd}" for priority in priority_primitives])

lsd = "["
rsd = "]"
done_str = "done"
doing_str = "doing"
todo_str = "todo"
hold_str = "hold"
status_primitives = (todo_str, doing_str, hold_str, done_str)
statuses_pretty = tuple([f"{lsd}{status}{rsd}" for status in status_primitives])

notes_dir_str = "notes"

all_delimiters = (lpd, rpd, lsd, rsd, "/")

task_extension = ".md"
schedule_extension = ".json"

editor = "vim"

print_separator = "-"*30

schedule_fname = f"schedule{schedule_extension}"
schedule_all_projects_key = "all"
default_schedule = {
    day: schedule_all_projects_key for day in
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}

valid_project_ids = list(string.ascii_lowercase)

