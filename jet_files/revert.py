import os
from jet_files import helper_functions as hf
import sys


def revert():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 4:
        print "Please form revert commands by typing" \
              " '$jet revert <branch_name> <commit_number>' \n" \
              "Remember the default branch is called 'master'"
        return

    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        if not sys.argv[2] == 'master':
            if not os.path.exists(os.path.join(branches_path + sys.argv[2])):
                print "Invalid branch name, aborting revert"
                print "Please form revert commands by typing" \
                      " '$jet revert <branch_name> <commit_number>' \n" \
                      "Remember the default branch is called 'master'"
                return

    if hf.is_valid_commit_number(sys.argv[3], sys.argv[2]):
        response = raw_input("Revert changes all your files back to the "
                             "point they were in at the commit number "
                             "specified. Any changes that are not committed"
                             " will be lost forever. \nAre you sure you wish"
                             " to revert? (yes/no) ")
        if response == 'yes' or response == 'y':
            print "Reverting....please wait..."
            hf.revert(sys.argv[2], sys.argv[3])
            print "Revert finished. You are now at the state of " \
                  "commit number %s in branch %s" % (sys.argv[3], sys.argv[2])
        elif response == 'no' or response == 'n':
            print "Cancelling revert"
        else:
            print "Invalid response, cancelling"
    else:
        print "Commit number is invalid, aborting revert."
        print "Please form revert commands by typing" \
              " '$jet revert <branch_name> <commit_number>' \n" \
              "Remember the default branch is called 'master'"


def run():
    revert()
