#!/usr/bin/python
import sys
import os
from os import walk
import hashlib

#called when file called
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)


def push():
    if not already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "Pushed"

def pull():
    if not already_initialized():
       print "Please init a jet repo before calling other commands"
       return
    print checksum_md5("one.py")
    print "Pulled"


def list_commits():
    if not already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    valud=True
    try:
        commit_number = sys.argv[2]
        if commit_number == "0":
            print "Initial commit"
            return
    except IndexError:
        commits = get_immediate_subdirectories(os.path.join(os.getcwd() + '/.jet/'))
        print "List of all commits. Type '$jet list <commit_number>' to see more information"
        commits.reverse()
        for commit in commits:
           print "Commit number: %s" % commit
        return
    commits = get_immediate_subdirectories(os.path.join(os.getcwd() + '/.jet/'))
    found=False
    for commit in commits:
        if commit == commit_number:
            found=True
            with open ('.jet/%s/file_log.txt' % commit_number, 'r') as file_:
                lines = file_.read().splitlines()
            try:
                line_number = sys.argv[3]
                try:
                    line = lines[int(line_number)]
                    try:
                        with open('.jet/%s/%s/changes.txt' % (commit_number, line_number), 'r') as file_:
                            to_print = file_.read().splitlines()
                        print "Changes to file %s" % line
                        for line_to_print in to_print:
                            print "    %s" % line_to_print
                    except IOError:
                        print "That line number was not an edited file, therefore there is no more information on it"
                except IndexError, TypeError:
                    print "Incorrect line number, type '$jet list %s' to see the possible lines numbers." % commit_number
                return
            except IndexError:
                pass
            print "Changelog for commit number %s" % commit_number
            print ""
            count = 0
            for line in lines:
                print "Line number %s:    %s" % (count, line)
                count += 1
            print ""
            print "Type '$jet list %s <line_number>' to see more information about that change" % commit_number
            
    
    if not found:
        print "Incorrect commit number, type '$jet list' to see all commits"
    
def commit():
    if not already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    #print sys.argv[2]
    #print sys.argv[3]
    if len(sys.argv) != 4 or sys.argv[2]!= "-m":
        print "Commit commands need to be formed by typing: $jet commit -m \"Your message here\""
    else:
        if os.path.isfile(os.path.join(os.getcwd() + '/.jet/changeset.txt')):
            new_files_in_changeset = get_new_files_in_changeset()
            deleted_files_in_changeset = get_deleted_files_in_changeset()
            changed_files_in_changeset = get_changed_files_in_changeset()
            new_commit_number = get_new_commit_number()
            os.mkdir('.jet/%s/' % new_commit_number)
            counter = 0
            with open ('.jet/%s/file_log.txt' % new_commit_number, 'w') as file_:
                for file_to_add in new_files_in_changeset:
                    file_.write("+" + file_to_add + "\n")
                    counter += 1
                for file_to_add in deleted_files_in_changeset:
                    file_.write("-" + file_to_add + "\n")
                    counter +=1
                for file_to_add in changed_files_in_changeset:
                    file_.write("~" + file_to_add + "\n")

            
            for file_ in changed_files_in_changeset:
                os.mkdir('.jet/%s/%s' % (new_commit_number, counter))
                with open('.jet/%s/%s/changes.txt' % (new_commit_number, counter), 'w') as myFile:
                    myFile.write(get_change_description(file_))
                    counter += 1
          
                
            os.remove(os.path.join(os.getcwd() + '/.jet/changeset.txt'))

            lines = get_stored_files()
            lines.extend(new_files_in_changeset)
            to_keep = []
            for line in lines:
                if line not in deleted_files_in_changeset:
                    to_keep.append(line)
            os.remove(os.path.join(os.getcwd() + '/.jet/latest_saved_files'))
            with open('.jet/latest_saved_files', 'w') as file_:
                for file_to_add in to_keep:
                    file_.write(file_to_add + "~J/ET")
                    file_.write(checksum_md5(file_to_add) + "~J/ET")
            print "Commiting"
        else:
            print "Please add files to commit using jet add before commiting!"

def add():
    if not already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    # At the moment, adds all of the files, however will eventually be able to choose!
    print "Added to changeset"
    with open ('.jet/changeset.txt', 'w') as file_:
        for file_to_add in get_new_files():
            file_.write("+" + file_to_add + "\n")
        for file_to_add in get_deleted_files():
            file_.write("-" + file_to_add + "\n")
        for file_to_add in get_changed_files():
            file_.write("~" + file_to_add + "\n")

def merge():
    if not already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "Merged"

def status():
    if not already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(get_current_files()) == len(get_stored_files()) and len(get_changed_files()) == 0:
        print "Nothing has changed!"
    else:
        print "Your repo has changed since the last commit"
        new_files = get_new_files()
        if new_files:
            new_files_in_changeset = get_new_files_in_changeset()
            if new_files_in_changeset:
                unadded_new = []
                for new_file in new_files:
                    if new_file not in new_files_in_changeset:
                        unadded_new.append(new_file)
                print "New files in changeset:"
                for new_file_in_changeset in new_files_in_changeset:
                    print "    %s" % new_file_in_changeset
            else:
                unadded_new = new_files
            if unadded_new:
                print "New files:"
                for new_file in unadded_new:
                    print "    %s" % new_file
        deleted_files = get_deleted_files()
        if deleted_files:
            deleted_files_in_changeset = get_deleted_files_in_changeset()
            if deleted_files_in_changeset:
                unadded_deleted = []
                for deleted_file in deleted_files:
                    if deleted_file not in deleted_files_in_changeset:
                        unadded_deleted.append(deleted_file)
                print "Deleted files in changeset:"
                for deleted_file_in_changeset in deleted_files_in_changeset:
                    print "    %s" % deleted_file_in_changeset
            else:
                unadded_deleted = deleted_files
            if unadded_deleted:
                print "Deleted files:"
                for deleted_file in unadded_deleted:
                    print "    %s" % deleted_file
    
    changed_files = get_changed_files()
    if changed_files:
        changed_files_in_changeset = get_changed_files_in_changeset()
        if changed_files_in_changeset:
            unadded = []
            for file_ in changed_files:
                if file_ not in changed_files_in_changeset:
                    unadded.append(file_)
            print "Changed files in changeset:"
            for changed_file_in_changeset in changed_files_in_changeset:
                print "    %s" % changed_file_in_changeset
        else:
            unadded = changed_files
        if unadded:
            print "Changed files:"
            for changed_file in unadded:
                print "    %s" % changed_file

def help_text():
    if not already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "For help, please visit www.jet.com/help"

def init():
    if already_initialized():
        print "Already a repo initialized"
    else:
        os.mkdir('.jet')
        f = []
        for (dirpath, dirnames, filenames) in walk(os.getcwd()):
            for filename in filenames:
                if not filename.endswith("~"):
                    f.append(os.path.join(dirpath, filename))
        with open('.jet/latest_saved_files', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "~J/ET")
                file_.write(checksum_md5(file_to_add) + "~J/ET")
        os.mkdir('.jet/0/')
        with open('.jet/0/file_list.txt', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "\n")

        print "Initializing Jet repository in %s" % os.getcwd()

def get_immediate_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]

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
        if file_to_check not in jet_files and not file_to_check.endswith("~"):
            current_files.append(file_to_check)
    #print current_files
    return current_files


def get_new_commit_number():
    commits = get_immediate_subdirectories(os.path.join(os.getcwd() + '/.jet/'))
    latest = commits[-1]
    int_latest = int(latest)
    new_commit_number = int_latest + 1
    return new_commit_number


def get_stored_files_and_hashes():
    #~J/E\T is the keyword sepertaing files                                              
    with open('.jet/latest_saved_files', 'r') as myFile:
        data = myFile.read().replace('\n', '')
    word = []
    lines = []
    code = []
    for char in data:
        if char == "~" and len(code) == 0:
            code.append(char)
        elif char == "J" and len(code) == 1:
            code.append(char)
        elif char == "/" and len(code) == 2:
            code.append(char)
        elif char == "E" and len(code) == 3:
            code.append(char)
        elif char == "T" and len(code) == 4:
            code.append(char)
            new_line = ''.join(word)
            lines.append(new_line)
            word = []
            code = []
        else:
            word.extend(code)
            code = []
            word.append(char)

    return lines

def get_stored_files():
    lines = get_stored_files_and_hashes()
    return lines[::2]

def get_stored_hash(filename):
    stored_files = get_stored_files_and_hashes()
    return_next = False
    for stored_file in stored_files:
        if return_next:
            return stored_file
        if stored_file == filename:
            return_next = True
    return False

def get_new_files():
    current_files = get_current_files()
    stored_files = get_stored_files()
    new_files = []
    for current_file in current_files:
        if current_file not in stored_files:
            new_files.append(current_file)
    return new_files

def get_new_files_in_changeset():
    try:
        with open('.jet/changeset.txt', 'r') as myFile:
            lines =myFile.read().splitlines()
    except IOError:
        return []
    new_files = []
    for line in lines:
        if line.startswith('+'):
            new_files.append(line[1:])
    return new_files



def get_deleted_files_in_changeset():
    try:
        with open('.jet/changeset.txt', 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return []
    deleted_files = []
    for line in lines:
        if line.startswith('-'):
            deleted_files.append(line[1:])
    return deleted_files


def get_changed_files_in_changeset():
    try:
        with open('.jet/changeset.txt', 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return []
    changed_files = []
    for line in lines:
        if line.startswith('~'):
            changed_files.append(line[1:])
    return changed_files

def get_deleted_files():
    current_files = get_current_files()
    stored_files = get_stored_files()
    deleted_files = []
    for stored_file in stored_files:
        if stored_file not in current_files:
            deleted_files.append(stored_file)
    return deleted_files

def already_initialized():
    directory = os.getcwd()
    already_done = False
    for filename in os.listdir(directory):
        if filename == ".jet":
            already_done = True
    return already_done

def checksum_md5(filename):
    md5 = hashlib.md5()
    with open(filename,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), b''): 
            md5.update(chunk)
    return md5.digest()


def get_changed_files():
    current_files = get_current_files()
    changed_files = []
    for file_to_compare in current_files:
        if not checksum_md5(file_to_compare) == get_stored_hash(file_to_compare):
            changed_files.append(file_to_compare)
#    print changed_files
    return changed_files

def get_change_description(filename):
    return "File was changed"

commands = {
    "add": add,
    "push": push,
    "pull": pull,
    "commit": commit,
    "merge": merge,
    "status": status,
    "init": init,
    "help": help_text,
    "list": list_commits,
}
try:
    commands[sys.argv[1]]()
except (KeyError):
    print "Invalid Command - Please set www.jet.com/commands for more info!"
except (IndexError):
    print "Not enough arguments"

