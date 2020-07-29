import os

'''
# Top level commands
--------------------
dex init [root path]                 # create a new schedule file and save the path somewhere
dex work                             # print and start work on the highest importance task, printing project_id+tid and all info
dex info                             # output some info about the current projects
dex example                          # create an example directory and set the current project to it

# Schedule commands
-------------------
dex schedule                          # view weekly schedule
dex schedule edit                     # edit the schedule file


# Project commands
-------------------
dex project                                 # make a new project
dex projects                                # show all projects, ordered by sum of importances of tasks
dex project [project_id] work               # work on a task, only for this project
dex project [project_id] view               # view a projects tasks in order of importance
dex project [project_id] prio               # +/- priority of all tasks for a particular project
dex project [project_id] rename             # rename a project
dex project [project_id] rm                 # delete a project



# Task commands
-------------------
dex task                              # make a new task
dex tasks                             # view ordered tasks across all projects
    (--by-project/-p)
    (--number/-n [val])
    
dex task [task_id] set ...
    (--importance/-i [val]) 
    (--efort/-e [val]) 
    (--due/-d [val) 
    (--status/-s [status])
    (--recurring/-r [days])
dex task [task_id] view
dex task [task_id] edit
dex task [task_id] rename


# Task aliases
-------------------
dex task [task_id] imp [val]
dex task [task_id] eff [val]
dex task [task_id] due [val] 
    (--recurring/-r [days])

dex task [task_id] work
dex task [task_id] done
dex task [task_id] todo
dex task [task_id] hold
dex task [task_id] aban <<alias for abandon>>

'''