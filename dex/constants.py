import os
import string

import mdv

dexcode_delimiter_left = "{["
dexcode_delimiter_right = "]}"
dexcode_delimiter_mid = "."
dexcode_header = "######dexcode:"

effort_primitives = (1, 2, 3, 4, 5)
importance_primitives = (1, 2, 3, 4, 5)
due_date_fmt = "%Y-%m-%d"


hold_str = "hold"
todo_str = "todo"
ip_str = "ip"
done_str = "done"
abandoned_str = "abandoned"
status_primitives = (hold_str, todo_str, ip_str, done_str, abandoned_str)
status_primitives_ints = {i: s for i, s in enumerate(status_primitives)}
status_primitives_ints_inverted = {v: k for k, v in status_primitives_ints.items()}

dexcode_delimiter_flag = "&"
no_flags, recurring_flag = flags_primitives = ["r", "n"]

tasks_subdir = "tasks"
notes_subdir = "notes"
done_subdir = "done"

task_extension = ".md"
schedule_extension = ".json"
print_separator = "-"*30

editor = "vim"


schedule_fname = f"schedule{schedule_extension}"
schedule_all_projects_key = "all"
default_schedule = {
    day: schedule_all_projects_key for day in
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}

valid_project_ids = list(string.ascii_lowercase)

thisdir = os.path.abspath(os.path.dirname(__file__))
reference_projset_path = os.path.join(thisdir, "../assets/reference_schedule")
