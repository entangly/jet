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

def add():
    # At the moment, adds all of the files, however will eventually be able to choose!
    print "Added to changeset"

def merge():
    print "Merged"

def status():
    if len(get_current_files()) == len(get_stored_files()):
        print "Nothing has changed!"
    else:
        print "Your repo has changed since the last commit"
        print "You have added:"
        for new_file in get_new_files():
            print "    %s" % new_file
        print "You have deleted:"
        for deleted_file in get_deleted_files():
            print "    %s" % deleted_file
        

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
            for filename in filenames:
                f.append(os.path.join(dirpath, filename))
        with open('.jet/current_files.txt', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "\n")

        print "Initializing Jet repository in %s" % directory

def get_current_files():
    file_list = []
    for (dirpath, dirnames, filenames) in walk(os.getcwd()):
        for filename in filenames:
            file_list.append(os.path.join(dirpath, filename))
        #print "Dirpath %s" % dirpath
        #print "dirname %s" % dirnames
        #print "filenames %s" % filenames
    jet_files = []
    for (dirpath, dirnames, filenames) in walk(os.path.join(os.getcwd(),'.jet/')):
        for filename in filenames:
            jet_files.append(os.path.join(dirpath, filename))

    #print file_list
    #print jet_files

    current_files = []
    for file_to_check in file_list:
        if file_to_check not in jet_files:
            current_files.append(file_to_check)
    #print current_files
    return current_files


def get_stored_files():
    with open('.jet/current_files.txt', 'r') as myFile:
        lines = myFile.read().splitlines()
        #print lines
        stored_files = []
        for line in lines:
            stored_files.append(line)
    return stored_files

def get_new_files():
    current_files = get_current_files()
    stored_files = get_stored_files()
    new_files = []
    for current_file in current_files:
        if current_file not in stored_files:
            new_files.append(current_file)
    return new_files

def get_deleted_files():
    current_files = get_current_files()
    stored_files = get_stored_files()
    deleted_files = []
    for stored_file in stored_files:
        if stored_file not in current_files:
            deleted_files.append(stored_file)
    return deleted_files












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

