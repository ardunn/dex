import os

'''
# Top level commands
--------------------
dex init [root path]                                # create a new executor file and save the path somewhere
dex work                                            # print and start work on the highest importance task, printing all info
dex info                                            # output some info about the current projects
dex example                                         # create an example directory and set the current project to it

dex tasks                                           # view ordered tasks across projects (default relevant to today, ordered by computed priority)
    Filtering (exclusive) options
    (--by-importance/-i)                            # Tasks ranked strictly by importance
    (--by-effort/-e)                                # Tasks ranked strictly by effort
    (--by-due/-d)                                   # Tasks ranked strictly by due date
    (--by-status/-s)                                # Tasks organized by status, ranked internally by computed priority
    (--by-project/-p)                               # Tasks organized by project, ranked internally by computed priority
    
    Additional options
    (--n-shown/-n [val])                            # limit to this number of total tasks shown
    (--all)                                         # show across all projects, not just today


# Executor commands
-------------------
dex exec view                                       # view weekly schedule
dex exec edit                                       # edit the schedule file


# Project commands
-------------------           
dex project new                                     # make a new project
dex project [id] exec                               # work on this specific project (not recommended)
dex project [id] view                               # show all tasks for this project, ordered by priority             
dex project [id] rename                             # rename a project
dex project [id] rm                                 # delete a project


# Task commands
-------------------
dex task                                            # make a new task
    
dex task [dexid] set ...                            # set an attribute of a task
    (--importance/-i [val]) 
    (--efort/-e [val]) 
    (--due/-d [val) 
    (--status/-s [status])
    (--recurring/-r [days])

dex task [dexid] view                               # view a task
dex task [dexid] edit                               # edit a task
dex task [dexid] rename                             # rename a task


# Task aliases
-------------------
dex task [dexid] imp [val]
dex task [dexid] eff [val]
dex task [dexid] due [val] 
    (--recurring/-r [days])

dex task [dexid] work
dex task [dexid] done
dex task [dexid] todo
dex task [dexid] hold
dex task [dexid] aban <<alias for abandon>>
'''