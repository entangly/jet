#!/usr/bin/python
import sys
import os
from os import walk
#called when file called
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)


def push():
    print "Pushed"

def pull():
    print "Pulled"

def commit():
    print sys.argv[2]
    print sys.argv[3]
    if len(sys.argv) != 4 or sys.argv[2]!= "-m":
        print "Commit commands need to be formed by typing: $jet commit -m \"Your message here\""
    else:
        print "Commited"

def merge():
    print "Merged"

def status():
    f = []
    for (dirpath, dirnames, filenames) in walk(os.getcwd()):
        f.extend(filenames)
    with open('.jet/current_files.txt', 'r') as myFile:
        stored_files = []
        for line in myFile:
            stored_files.append(line)
    jet_files = []
    for (dirpath, dirnames, filenames) in walk('.jet/'):
        jet_files.extend(filenames)
    current_files = []
    for file_to_check in f:
        if file_to_check not in jet_files:
            current_files.append(file_to_check)
    if len(current_files) == len(stored_files):
        print "No files changed"
    else:
        new_files = []
        deleted_files = []
        for current_file in current_files:
            if current_file not in stored_files:
                new_files.append(current_file)
        for stored_file in stored_files:
            if stored_file not in current_files:
                deleted_files.append(stored_file)
        print "Your repo has changed since the last commit"
        print "You have added:"
        for new_file in new_files:
            print "    %s" % new_file
        print "You have deleted:"
        for deleted_file in deleted_files:
            print "    %s" % old_file
        

def init():
    directory = os.getcwd()
    already_done = False
    for filename in os.listdir(directory):
        if filename == ".jet":
            already_done = True
    if already_done:
        print "Already a repo initialized"
    else:
        os.mkdir('.jet')
        f = []
        for (dirpath, dirnames, filenames) in walk(os.getcwd()):
            f.extend(filenames)
        with open('.jet/current_files.txt', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add)

        print "Initializing Jet repository in %s" % directory

commands = {
    "push": push,
    "pull": pull,
    "commit": commit,
    "merge": merge,
    "status": status,
    "init": init,
}

try:
    commands[sys.argv[1]]()
except (KeyError):
    print "Invalid Command - Please set www.jet.com/commands for more info!"
except (IndexError):
    print "Not enough arguments"
