import os
import sys
from jet_files import (status,
                       push,
                       pull,
                       list_commits,
                       commit_changeset,
                       init,
                       add,
                       merge,
                       help_text,
                       local_tests,
                       helper_functions,
                       login,
                       revert,
                       hook,
                       branch)


commands = {
    "add": add.run,
    "push": push.run,
    "pull": pull.run,
    "commit": commit_changeset.run,
    "merge": merge.run,
    "status": status.run,
    "init": init.run,
    "help": help_text.run,
    "list": list_commits.run,
    "test": local_tests.run,
    "login": login.run,
    "hook": hook.run,
    "branch": branch.run,
    "revert": revert.run,
}
try:
    commands[sys.argv[1]]()
except KeyError:
    print "Invalid Command - Please set www.jetvc.co.uk/commands for more info!"
except IndexError:
    print "Not enough arguments"

