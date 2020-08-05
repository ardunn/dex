import os
import string
import datetime

dexcode_delimiter_left = "{["
dexcode_delimiter_right = "]}"
dexcode_delimiter_mid = "."
dexcode_header = "######dexcode:"

effort_primitives = (1, 2, 3, 4, 5)
importance_primitives = (1, 2, 3, 4, 5)
due_date_fmt = "%Y-%m-%d"

# max due date is 1 year in the future
max_due_date = datetime.datetime.today() + datetime.timedelta(days=365)
today_in_executor_format = datetime.datetime.today().strftime("%A")


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
inactive_subdir = f"{abandoned_str}+{done_str}"

task_extension = ".md"
note_extension = ".md"
executor_extension = ".json"
print_separator = "-"*30


executor_fname = f"executor{executor_extension}"
executor_all_projects_key = "all"
default_executor = {
    day: executor_all_projects_key for day in
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}

valid_project_ids = list(string.ascii_lowercase)

