import os
import sys
from jet_files import helper_functions as hf
from jet_files import commit_changeset, add


def merge():
    # merging is based on
    # http://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if not len(sys.argv) == 3:
        print "Please form merge commands '$jet merge" \
              "<branch>' - where <branch> is the branch to merge into" \
              "the current one. \nThe merge will make a new commit" \
              " in the current branch"
        return
    filename = os.path.join(hf.get_jet_directory() + '/.jet/changeset.txt')
    changed_files = False
    if os.path.isfile(filename):
        changed_files = True
    if len(hf.get_changed_files()) > 0:
        changed_files = True
    if changed_files:
        print "You can't merge until you commit...."
        return
    branch = sys.argv[2]
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        if not os.path.exists(os.path.join(branches_path + sys.argv[2])):
            print "Invalid branch name, please try again."
            return

    hf.merge(branch)
    add.add(verbose=False)
    commit_changeset.commit("Merged branch %s into branch %s."
                            % (branch, hf.get_branch()), verbose=False)
    commit_number_used = hf.get_new_commit_number() - 1
    print "Merged branch %s into branch current branch %s." \
          "\nCommitted merge with commit number %s." % (hf.get_branch(),
                                                        branch,
                                                        commit_number_used)


def run():
    merge()