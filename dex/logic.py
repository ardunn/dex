import pprint



## name, effort, due, importance, status

tasks = {
    "t1: file stuff for graduation": [1, 2, 5, "todo"],
    "t2: write final project report": [5, 22, 4, "ip"],
    "t3: finish internship application": [1, 14, 4, "ip"],
    "t4: turn in chemistry homework": [2, 8, 3, "ip"],
    "t5: email TA": [1, 11, 1, "todo"]
}



# todo: account for negative due date/overdue tasks
# todo: try normalizing importances and efforts

# higher is higher priority
def priority_score(task):
    e, d, i, s = task

    s_factor = 1.2 if s == "ip" else 1
    p = i ** 2 * s_factor * e/d
    return p



tasks_ranked = []
for task_name, task in tasks.items():
    tasks_ranked.append((task_name, priority_score(task)))

tasks_ranked.sort(key=lambda t: t[1])

pprint.pprint(tasks_ranked)