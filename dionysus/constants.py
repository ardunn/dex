lpd = "{"
rpd = "}"
priority_primitives = list(range(3))
priorities_pretty = tuple([f"{lpd}{priority}{rpd}" for priority in priority_primitives])

lsd = "["
rsd = "]"
status_primitives = ("todo", "doing", "done")
statuses_pretty = tuple([f"{lsd}{status}{rsd}" for status in status_primitives])


all_delimiters = (lpd, rpd, lsd, rsd)

task_extension = ".md"
schedule_extension = ".json"

editor = "vim"

