from jet_files import helper_functions as hf


def diff():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return


def run():
    diff()