#!/usr/bin/python
import sys

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
    print "Initializing Jet repository"

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
    print "Not enough arguements"
