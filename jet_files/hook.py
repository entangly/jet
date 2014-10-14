import os
import helper_functions as hf
import sys


def hook():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 4:
        print "Sorry, but that is not a recognized Jet command. Please" \
              " either type '$ jet hook <commit|push> inspect' to see " \
              "what hooks you already have, or type '$ jet hook <commit|pu" \
              "sh> <script_name>' " \
              "to add a hook!"
        return
    if sys.argv[3] == 'inspect':
        filename = (hf.get_branch_location() + 'hooks')
        if sys.argv[2] == 'commit' or sys.argv[2] == 'push':
            try:
                with open(filename, 'r') as file_:
                    lines = file_.read().splitlines()
            except IOError:
                print "You have no hooks on the %s command" % sys.argv[2]
                return
            try:
                if lines[0] == sys.argv[2]:
                    print "The %s command is hooked by:" % sys.argv[2]
                    print "    %s" % lines[1]
            except IndexError:
                print "You have no hooks on the %s command" % sys.argv[2]
            try:
                if lines[2] == sys.argv[2]:
                    print "The %s command is hooked by:" % sys.argv[2]
                    print "    %s" % lines[3]
            except IndexError:
                print "You have no hooks on the %s command" % sys.argv[2]
        else:
            print "Command isn't recognized by Jet, please form inspect" \
                  "commands like '$ jet hook <commit|push> inspect'"
    elif sys.argv[3] == 'remove':
        if sys.argv[2] == 'commit' or sys.argv[2] == 'push':
            filename = (hf.get_branch_location() + 'hooks')
            to_keep = []
            try:
                with open(filename, 'r') as file_:
                    lines = file_.read().splitlines()
                if not lines[0] == sys.argv[2]:
                    to_keep.append(lines[0])
                    to_keep.append(lines[1])
                    print "Successfully removed the %s hook" % sys.argv[2]
                if not lines[2] == sys.argv[2]:
                    to_keep.append(lines[2])
                    to_keep.append(lines[3])
                    print "Successfully removed the %s hook" % sys.argv[2]
            except IOError:
                to_keep.append("")
                to_keep.append("")
            except IndexError:
                to_keep.append("")
                to_keep.append("")

            with open(filename, 'w') as myFile:
                myFile.write(to_keep[0] + '\n')
                myFile.write(to_keep[1] + '\n')

        else:
            print "Command isn't recognized by Jet, please form inspect" \
                  "commands like '$ jet hook <commit|push> remove'"
    else:
        if not os.path.isfile(sys.argv[3]):
            print "Couldn't add hook, unrecognized file!"
        else:
            if sys.argv[2] == 'commit' or sys.argv[2] == 'push':
                filename = (hf.get_branch_location() + 'hooks')
                to_keep = []
                try:
                    with open(filename, 'r') as file_:
                        lines = file_.read().splitlines()
                    if not lines[0] == sys.argv[2]:
                        to_keep.append(lines[0])
                        to_keep.append(lines[1])
                        print "Successfully added the %s hook" % sys.argv[2]
                    if not lines[2] == sys.argv[2]:
                        to_keep.append(lines[2])
                        to_keep.append(lines[3])
                        print "Successfully added the %s hook" % sys.argv[2]
                except IOError:
                    to_keep.append("")
                    to_keep.append("")
                    print "Successfully added the %s hook" % sys.argv[2]
                except IndexError:
                    to_keep.append("")
                    to_keep.append("")

                with open(filename, 'w') as myFile:
                    myFile.write(sys.argv[2] + '\n')
                    myFile.write(sys.argv[3] + '\n')
                    myFile.write(to_keep[0] + '\n')
                    myFile.write(to_keep[1] + '\n')

            else:
                print "Command isn't recognized by Jet, please form " \
                      "commands like '$ jet hook <commit|push> <script_name>'"


def run():
    hook()