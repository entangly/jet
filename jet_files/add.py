import os
from jet_files import helper_functions as hf


def add(verbose):
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    # At the moment, adds all of the files, however will be able to choose!
    if verbose:
        print "Added to changeset"
    filename = os.path.join(hf.get_branch_location() + 'changeset.txt')
    with open(filename, 'w') as file_:
        for file_to_add in hf.get_new_files():
            file_.write("+" + file_to_add + "\n")
        for file_to_add in hf.get_deleted_files():
            file_.write("-" + file_to_add + "\n")
        for file_to_add in hf.get_changed_files():
            file_.write("~" + file_to_add + "\n")


def run():
    add(verbose=True)