import sys
import os
import helper_functions as hf


def login():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 3:
        print "To login, type: \n    $jet login <username> \nThis could" \
              " be the username you use on www.jetvc.co.uk or one you" \
              " wish to put with your commits"
    else:
        username = sys.argv[2]
        filename = os.path.join(hf.get_jet_directory()
                                + '/.jet/username')
        with open(filename, 'w') as file_:
            file_.write(username)
        print hf.BColors.GREEN + "Welcome %s" % username + hf.BColors.ENDC


def run():
    login()