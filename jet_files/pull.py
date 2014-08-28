from jet_files import helper_functions as hf


def pull():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "Pulled"


def run():
    pull()