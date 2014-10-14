from jet_files import helper_functions as hf


def push():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if not hf.logged_in():
        print "You must login before pushing! To do this type:" \
              " $jet login <username>"
        return
    hook = hf.get_push_hook()
    if hook:
        result = hf.run_hook(hook)
        if result:
            print "Hook passed."
        else:
            print "Hook Failed. Not pushing"
            return
    print "Pushed"


def run():
    push()