lpd = "("
rpd = ")"
priority_regex = f"\{lpd}(.*)\{rpd}"
priority_keyword = "priority"

lsd = "["
rsd = "]"
status_regex = f"\{lsd}(.*)\{rsd}"
status_mapping = {
    "1 - todo": "todo",
    "2 - doing": "doing",
    "3 - done": "done"
}

status_mapping_inverted = {v: k for k, v in status_mapping.items()}

task_extension = ".md"
schedule_extension = ".json"

editor = "vim"