import os
import sys
from jet_files import helper_functions as hf


def diff():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 5:
        print "Please form diff commands " \
              "'$jet diff <filename> <branch> <commit_number>'"
    if os.path.exists(sys.argv[2]):
        full_file_name = os.path.join(os.getcwd() + '/' + sys.argv[2])
        old_file = hf.get_file_at(sys.argv[3], sys.argv[4], full_file_name)
        if old_file is None:
            print "File could not be found at the point specified"
            return
        with open(full_file_name, 'r') as file_:
            current_file = file_.read().splitlines()
        difference = hf.diff(old_file, current_file)
        print difference
    else:
        print "Invalid filename."


def run():
    diff()