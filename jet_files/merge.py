import sys
from jet_files import helper_functions as hf


def merge():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if not len(sys.argv) == 4:
        print "Please form merge commands '$jet merge" \
              " <branch_from> <branch_to>' "
    branch_from = sys.argv[2]
    branch_to = sys.argv[3]
    print "Merged branch %s into branch %s." \
          "\nCommitted merge to branch %s." % (branch_from,
                                               branch_to,
                                               branch_to)


def run():
    merge()