import sys
from jet_files import (status,
                       push,
                       pull,
                       list_commits,
                       commit_changeset,
                       init,
                       add,
                       merge,
                       help_text)


def jet_push():
    push.run()


def jet_pull():
    pull.run()


def jet_list_commits():
    list_commits.run()


def jet_commit_changeset():
    commit_changeset.run()


def jet_add():
    add.run()


def jet_merge():
    merge.run()


def jet_status():
    status.run()


def jet_help_text():
    help_text.run()


def jet_init():
    init.run()

commands = {
    "add": jet_add,
    "push": jet_push,
    "pull": jet_pull,
    "commit": jet_commit_changeset,
    "merge": jet_merge,
    "status": jet_status,
    "init": jet_init,
    "help": jet_help_text,
    "list": jet_list_commits,
}
try:
    commands[sys.argv[1]]()
except KeyError:
    print "Invalid Command - Please set www.jet.com/commands for more info!"
except IndexError:
    print "Not enough arguments"


# from jet_files import helper_functions
# print helper_functions.get_jet_directory()