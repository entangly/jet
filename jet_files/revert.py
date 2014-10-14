from jet_files import helper_functions as hf
import sys


def revert():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 3:
        print "Please form revert commands by typing" \
              " $jet revert <commit_number>"
        return

    if hf.is_valid_commit_number(sys.argv[2]):
        response = raw_input("Revert changes all your files back to the "
                             "point they were in at the commit number "
                             "specified. Any changes that are not committed"
                             " will be lost forever. \nAre you sure you wish"
                             " to revert? (yes/no) ")
        if response == 'yes' or response == 'y':
            print "Reverting....please wait..."
            hf.revert(sys.argv[2])
        elif response == 'no' or response == 'n':
            print "Cancelling revert"
        else:
            print "Invalid response, cancelling"
    else:
        print "Commit number is invalid, cannot revert."



def run():
    revert()