from jet_files import helper_functions as hf


def help_text():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "For help, please visit www.jet.com/help"


def run():
    help_text()