import os
from jet_files import helper_functions as hf


# At the moment, all files are added to the changeset, issue raised to change
def add(verbose):
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return

    filename = os.path.join(hf.get_branch_location() + 'changeset.txt')
    with open(filename, 'w') as file_:
        for file_to_add in hf.get_new_files():
            file_.write("+" + file_to_add + "\n")
        for file_to_add in hf.get_deleted_files():
            file_.write("-" + file_to_add + "\n")
        for file_to_add in hf.get_changed_files():
            file_.write("~" + file_to_add + "\n")

    if verbose:
        print "Added to changeset"


def run():
    add(verbose=True)
