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
                       helper_functions)


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


def test():
    local_tests.run()


def login():
    if not helper_functions.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 3:
        print "To login, type: \n    $jet login <username> \nThis could be the " \
              "username you use on www.jetvc.co.uk or one you" \
              " wish to put with your commits"
    else:
        username = sys.argv[2]
        filename = os.path.join(helper_functions.get_jet_directory()
                                + '/.jet/username')
        with open(filename, 'w') as file_:
            file_.write(username)
        print "Welcome %s" % username

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
    "test": test,
    "login": login,
}
try:
    commands[sys.argv[1]]()
except KeyError:
    print "Invalid Command - Please set www.jet.com/commands for more info!"
except IndexError:
    print "Not enough arguments"

