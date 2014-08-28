from jet_files import helper_functions as hf


def push():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "Pushed"


def run():
    push()