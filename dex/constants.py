import os
import string

import mdv

dexcode_delimiter_left = "{["
dexcode_delimiter_right = "]}"
dexcode_delimiter_mid = "."

effort_primitives = (1, 2, 3, 4, 5)
importance_primitives = (1, 2, 3, 4, 5)
due_date_fmt = "%Y-%m-%d"
status_primitives = ("hold", "todo", "ip", "done", "abandoned")
status_primitives_ints = {0: "hold", 1: "todo", 2: "ip", 3: "done", 4: "abandoned"}
status_primitives_ints_inverted = {v: k for k, v in status_primitives_ints.items()}

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
