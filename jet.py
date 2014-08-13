#!/usr/bin/python
import sys
import os
#called when file called
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)


def push():
    print "Pushed"

def pull():
    print "Pulled"

def commit():
    print "Committed"

def merge():
    print "Merged"

def status():
    print "No files changed"

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
