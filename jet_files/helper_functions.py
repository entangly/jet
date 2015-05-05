import os
from os import walk
import hashlib
import subprocess


# This class represents the colours used to print (to the command line
# They can then be used by typing BColors.PINK etc
class BColors:
    def __init__(self):
        pass

    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


# This method gets the directory which is being
# version controlled. Eg: the root directory
def get_jet_directory():
    # Get the current directory.
    directory = os.getcwd()
    # Gets the parent directory
    parent = os.path.abspath(os.path.join(directory, os.pardir))
    # Set jet directory to blank, to show it's empty
    jet_directory = ""
    # Set found to false to show not yet there
    found = False
    while not directory == parent and jet_directory == "":
        for filename in os.listdir(directory):
            if filename == ".jet":
                found = True
        if found:
            jet_directory = directory
        else:
            directory = parent
            parent = os.path.abspath(os.path.join(directory, os.pardir))
    return jet_directory


# Gives the location where the data for the branch is stored
def get_branch_location():
    # Gets what branch you're on
    branch = get_branch()
    # Master is stored separately
    if branch == 'master':
        return os.path.join(get_jet_directory() + '/.jet/')
    else:
        return os.path.join(get_jet_directory() + '/.jet/branches/%s/'
                            % branch)


# Gives the location where the data is stored for the passed in branch
def get_branch_location_param(branch):
    # Master is stored separately
    if branch == 'master':
        return os.path.join(get_jet_directory() + '/.jet/')
    else:
        return os.path.join(get_jet_directory() + '/.jet/branches/%s/'
                            % branch)


# Gets all child directories of the parameter
def get_immediate_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


# Gets all the current files under the root folder
# Jet directory is optional parameter as will fetch otherwise
def get_current_files(jet_directory):
    if jet_directory is None:
        jet_directory = get_jet_directory()
    # Initialize the list to empty
    file_list = []
    for (dirpath, dirnames, filenames) in walk(jet_directory):
        # Ignore jet directory
        if '.jet' in dirpath:
            # Go to the next directory
            continue
        for filename in filenames:
            # Add all filenames to the list !
            file_list.append(os.path.join(dirpath, filename))
    
    # First, check none of the files are in the
    #  ignore file, as we are not interested in them
    return filter_files_by_ignore(file_list)


# Returns the next number that should be used
# for making a commit in the current branch
def get_new_commit_number():
    # Commits are stored in folders,
    # so get all the folders in the current branch
    commits = get_immediate_subdirectories(get_branch_location())
    try:
        # Irrelevant folder, try to remove it
        commits.remove('branches')
    except ValueError:
        pass
    # Current biggest starts at 0, only improve if more commits found
    biggest = 0
    # Loop through all the folders
    for commit in commits:
        try:
            # Get the folders name as a integer
            commit_num = int(commit)
            # If it's larger, update the biggest variable
            if commit_num > biggest:
                biggest = commit_num
        # ValueError means it wasn't a commit folder, so ignore
        except ValueError:
            pass
    # Ensure the biggest is an integer
    int_latest = int(biggest)
    # Increment by one
    new_commit_number = int_latest + 1
    return new_commit_number


# Returns a copy of the file which
# contains the last saved files and hashes as a list
def get_stored_files_and_hashes():
    filename = os.path.join(get_branch_location() + 'latest_saved_files')
    with open(filename, 'r') as myFile:
        data = myFile.read().splitlines()
    return data


# Takes the stored files and hashes, and only returns the filenames
# The lines parameter is optional,
#  and should be the result of get_stored_files_and_hashes()
def get_stored_files(lines):
    if lines is None:
        lines = get_stored_files_and_hashes()
    return lines[::2]


# Gets the hash of the file passed in, at the last point stored
# The stored_files_and_hashes parameter is optional and used to save re-fetching
def get_stored_hash(filename, stored_files_and_hashes):
    if not stored_files_and_hashes:
        stored_files_and_hashes = get_stored_files_and_hashes()
    # Once the filename has been found, the next item in the list is
    # the corresponding hash,  so return that. 
    return_next = False
    for line in stored_files_and_hashes:
        if return_next:
            return line
        if line == filename:
            return_next = True
    # Return false if filename not in the list. 
    return False


# Gets all the files in the directory, that are not in the list of stored files. 
# The lists of files parameters are optional and will be fetched if not given
def get_new_files(current_files, stored_files):
    if current_files is None:
        current_files = get_current_files(None)
    if stored_files is None:
        stored_files = get_stored_files(None)
    return [x for x in current_files if x not in stored_files]


# Gets a list of all the files that have been added to the changeset.
# Branch location is optional parameter and will be fetched if not given
def get_files_in_changeset(branch_location):
    if branch_location is None:
        branch_location = get_branch_location()
    try:
        # Open up the changeset file
        filename = os.path.join(branch_location + 'changeset.txt')
        with open(filename, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        # If there is no changeset file, means nothing added, so return empty list
        return []
    return lines


# Gets the files which are new to the repository and added to the changeset
# The lines parameter is optional and is fetched from the file if not provided
def get_new_files_in_changeset(lines):
    if lines is None:
        try:
            # Opens up the changeset file
            filename = os.path.join(get_branch_location() + 'changeset.txt')
            with open(filename, 'r') as myFile:
                lines = myFile.read().splitlines()
        except IOError:
            # If no changeset file, then no new files added, so return empty
            return []
    
    new_files = []
    # Loop through all the filenames
    for line in lines:
        # If it starts with a plus, then it's a new file 
        if line.startswith('+'):
            new_files.append(line[1:])
    return new_files


# Gets the files which are deleted from the repository and added to the changeset
# The lines parameter is optional and is fetched from the file if not provided
def get_deleted_files_in_changeset(lines):
    if lines is None:
        try:
            # Opens up the changeset file
            filename = os.path.join(get_branch_location() + 'changeset.txt')
            with open(filename, 'r') as myFile:
                lines = myFile.read().splitlines()
        except IOError:
            # If no changeset file, then no deleted files added, so return empty
            return []
    deleted_files = []
    # Loop through all the filenames
    for line in lines:
        # If it starts with a subtract, then it's a deleted file
        if line.startswith('-'):
            deleted_files.append(line[1:])
    return deleted_files


# Gets the files which are changed from the repository and added to the changeset
# The lines parameter is optional and is fetched from the file if not provided
def get_changed_files_in_changeset(lines):
    if lines is None:
        try:
            # Opens up the changeset file
            filename = os.path.join(get_branch_location() + 'changeset.txt')
            with open(filename, 'r') as myFile:
                lines = myFile.read().splitlines()
        except IOError:
            # If no changeset file, then no changed files added, so return empty
            return []
    changed_files = []
    # Loop through all the filenames
    for line in lines:
        # If it starts with a tilde, then it's a deleted file
        if line.startswith('~'):
            changed_files.append(line[1:])
    return changed_files


# Gets all the files in the directory,
# that have been deleted since the last commit 
# The lists of files parameters are optional
# and will be fetched if not given
def get_deleted_files(current_files, stored_files):
    if current_files is None:
        current_files = get_current_files(None)
    if stored_files is None:
        stored_files = get_stored_files(None)
    deleted_files = []
    for stored_file in stored_files:
        if stored_file not in current_files:
            deleted_files.append(stored_file)
    return deleted_files


# Checks to see if the current directory, or any parents are initialized. 
# The jet directory is "" if there isn't one, so return False
def already_initialized():
    return not get_jet_directory() == ""


# Returns the md5 hash of the file given by the filename
def checksum_md5(filename):
    with open(filename, 'r') as f:
        contents = f.read()
    return hashlib.md5(contents).hexdigest()


# Gets all the files in the directory,
# that have been changed since the last commit 
# The lists of files parameters are optional
# and will be fetched if not given
def get_changed_files(current_files, stored_files_and_hashes):
    if current_files is None:
        current_files = get_current_files(None)
    changed_files = []
    for file_to_compare in current_files:
        if not checksum_md5(file_to_compare) ==\
                get_stored_hash(file_to_compare, stored_files_and_hashes):
            changed_files.append(file_to_compare)
    return changed_files


# This function processes the changes between the current state of 
# a file and the state at the previous commit. 
def get_change_description(filename):
    # As the commit folder has already been made for this commit,
    # Subtract 2 from what would be the next one, to get the previous.
    commit_number = get_new_commit_number() - 2
    # Get the previous state of the file
    previous_file = get_file_at(get_branch(), commit_number, filename)
    # If it can't be found, return None to signal error
    if previous_file is None:
        return None
    # Get the difference between the files.
    difference = diff(previous_file, filename)
    # If there's an error getting a diff, report it
    if not difference:
        return "Jet is sorry, but there was an error in processing the" \
               " changes for this file"
    else:
        # Otherwise, return the diff as the change description! 
        return difference


# This method calculates the difference
# between two files and returns it as a string
# The parameters can be passed in as an array or a filename.
def diff(file1, file2):
    # Gets both files into list format
    try:
        # Checks to see if it's a list
        if type(file1) == list:
            old_lines = file1
        else:
            # If it's not a list, it's a filename, so open the file
            with open(file1, 'r') as file_:
                old_lines = file_.read().splitlines()
        # Checks to see if the second input is a list
        if type(file2) == list:
            current_lines = file2
        else:
            # Otherwise, it's a filename, so open the file
            with open(file2, 'r') as file_:
                current_lines = file_.read().splitlines()
    # An IOError means invalid filename,
    # so a diff can therefore not be processed
    except IOError:
        # Return a standard error message in place of the diff.
        return "Jet is sorry, but there was an error in processing the" \
               " changes for this file"
    # To start with, the diff is blank, so initialize to empty string
    description = ""
    # Initialize all counters to -1,
    # as they're incremented at the start of the loop.
    line_number = -1
    count = -1
    old_count = -1
    # Loop until the pointer going through the old file,
    # reaches the end of the file
    while old_count < len(old_lines):
        # Increment all the pointers
        old_count += 1
        count += 1
        line_number += 1
        # Get the line once - index error shouldn't happen
        # but if it does, break the loop.
        try:
            line = old_lines[old_count]
        except IndexError:
            # Exit the loop
            break
        # Get the line we're comparing against in the current file
        try:
            current_lines[count]
        except IndexError:
            # Index error would mean that the line doesn't
            # exist in the current file
            # Therefore, that line has been deleted, so add
            # to the diff saying so
            description += ("(" + str(line_number) + ") " +
                            "- " +
                            line +
                            "\n")
            # Continue to the next line in the file
            continue
        
        # Lines being the same would assume no difference,
        # so only execute code that deals
        # with the lines being different
        if not current_lines[count] == line:
            # If the line in the old file is blank
            if line == "":
                # Add to the diff that the blank line was removed.
                description += ("(" + str(line_number) + ") " +
                                "- blank line\n")
                # Minus the counter, to take the missing line into account
                count -= 1
            else:
                # If the line is in the current file is blank
                if current_lines[count] == "":
                    # Add to the diff that the blank line was added.
                    description += ("(" + str(line_number) + ") " +
                                    "+ blank line\n")
                    # Minus the counter on the old file,
                    # to take the missing line into account
                    old_count -= 1
                else:
                    # Add to the diff the file has changed,
                    # and the new contents
                    description += ("(" + str(line_number) + ") " +
                                    "~ " + current_lines[count] + "\n")

    # While there is still content left in the current file,
    # as the counters are different
    while count <= len(current_lines) - 1:
        # If the line is blank
        if current_lines[count] == "":
            # Add a blank line to the diff,
            # as the current file has an additional one
            description += ("(" + str(line_number) + ") " +
                            "+ blank line\n")
        else:
            # Show the new line added in the diff
            description += ("(" + str(line_number) + ") " +
                            "+ " +
                            current_lines[count] +
                            "\n")
        # Increment the counters for the end of the current file
        line_number += 1
        count += 1

    # Due to blank lines at the end of files, last new line is un-needed
    description_to_return = description[:-1]
    # If nothing was different, alert them
    if description_to_return == "":
        return "No changes found"
    else:
        return description_to_return


# Jet stores each file change in numbered folders
# This gets the number of the folder for a specific file, at
# a specific commit and specific branch.
def get_file_change_number(branch, commit_number, filename):
    # Master branch content is stored elsewhere.
    if not branch == 'master':
        # Gets the list of files at that point
        file_list_file = os.path.join(get_jet_directory() +
                                      '/.jet/branches/%s/%s/file_log.txt'
                                      % (branch, commit_number))
    else:
        file_list_file = os.path.join(get_jet_directory() +
                                      '/.jet/%s/file_log.txt' % commit_number)
    with open(file_list_file, 'r') as myFile:
        file_list = myFile.read().splitlines()
    change_number = 0
    # Goes through the list of files, until the correct one is found
    for file_ in file_list:
        if file_ == filename or file_[1:] == filename:
            # Returns the changenumber once the file is found
            return change_number
        else:
            change_number += 1
    return None


def get_last_complete_file(branch, filename):
    change_number = None
    count = 0
    while change_number is None and count <= get_highest_commit(branch):
        change_number = get_file_change_number(branch, count, filename)
        count += 1
    count -= 1
    if count > 0:
        name_of_file = 'changes.txt'
    else:
        name_of_file = os.path.basename(filename)
    if not branch == 'master':
        modded_filename = os.path.join(get_jet_directory()
                                       + '/.jet/branches/%s/%s/%s/%s'
                                       % (branch, count,
                                          change_number, name_of_file))
    else:
        modded_filename = os.path.join(get_jet_directory() + '/.jet/%s/%s/%s'
                                       % (count, change_number, name_of_file))
    try:
        with open(modded_filename, 'r') as myFile:
                current_file = myFile.read().splitlines()
    except IOError:
        return None, None
    commit_number = 0
    return current_file, commit_number


def get_diff_at(branch, commit_number, filename):
    change_num = get_file_change_number(branch, commit_number, filename)
    if change_num is None:
        return []
    if not branch == 'master':
        modded_filename = os.path.join(get_jet_directory()
                                       + '/.jet/branches/%s/%s/%s/changes.txt'
                                       % (branch, commit_number, change_num))
    else:
        modded_filename = os.path.join(get_jet_directory()
                                       + '/.jet/%s/%s/changes.txt'
                                       % (commit_number, change_num))
    with open(modded_filename, 'r') as myFile:
        difference = myFile.read().splitlines()
    return difference


def get_file_at(branch, commit_number, filename):
    if not is_valid_commit_number(commit_number, branch):
        return None
    last_complete, last_full_commit = get_last_complete_file(branch, filename)
    if last_complete is None:
        return None
    commits_to_add = []
    commit = last_full_commit + 1
    if commit_number == '0' or commit_number == 0:
        return last_complete
    while not int(commit) == int(commit_number):
        commits_to_add.append(commit)
        commit += 1
    commits_to_add.append(commit)

    current_file = last_complete
    for c in commits_to_add:
        current_file = reform_file(current_file, get_diff_at(branch,
                                                             c,
                                                             filename))

    return current_file


def reform_file(_file_, diff_list):
    if type(_file_) == list:
        lines = _file_
    else:
        with open(_file_, 'r') as file_:
            lines = file_.read().splitlines()
    if len(diff_list) == 0:
        return lines
    if diff_list[0] == 'No changes found':
        return lines
    for d in diff_list:
        try:
            index = d.index(' ')
            line_number_list = d[1:index-1]
            line_number = ''
            for number in line_number_list:
                line_number += number
            count = int(line_number)
        except ValueError:
            if type(_file_) == list:
                lines = _file_
            else:
                with open(_file_, 'r') as file_:
                    lines = file_.read().splitlines()
            return lines
        action = d[index + 1]
        content = d[index + 3:]
        if action == '~':
            try:
                lines[count] = content
            except IndexError:
                pass
        elif action == '+':
            try:
                if content == 'blank line':
                    lines.insert(count, '')
                else:
                    lines.insert(count, content)
            except IndexError:
                pass
        elif action == '-':
            try:
                lines[count] = "~J/E\T DELETE ~J/E\T"
            except IndexError:
                pass

    to_return = []
    for line in lines:
        if not line == "~J/E\T DELETE ~J/E\T":
            to_return.append(line)
    return to_return


def get_username():
    filename = os.path.join(get_jet_directory() + '/.jet/username')
    try:
        with open(filename, 'r') as file_:
                    lines = file_.read().splitlines()
        username = lines[0]
    except IOError:
        username = ''
    except IndexError:
        os.remove(filename)
        username = ''
    return username


# Returns a boolean to see if user is logged in
def logged_in():
    return not get_username() == ''


def get_commit_hook():
    try:
        filename = (get_branch_location() + 'hooks')
        with open(filename, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return False
    try:
        if lines[0] == 'commit':
            return lines[1]
        elif lines[2] == 'commit':
            return lines[3]
        else:
            return False
    except IndexError:
        return False


def get_push_hook():
    try:
        filename = (get_branch_location() + 'hooks')
        with open(filename, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return False
    try:
        if lines[0] == 'push':
            return lines[1]
        elif lines[2] == 'push':
            return lines[3]
        else:
            return False
    except IndexError:
        return False


def run_hook(filename):
    # noinspection PyBroadException
    try:
        return_code = subprocess.call("python %s" % filename, shell=True)
    except Exception:
        return False
    if return_code == 0:
        return True
    else:
        return False


def is_valid_commit_number(number, branch):
    number = '%s' % number
    if branch is None:
        commits = get_immediate_subdirectories(get_branch_location())
    elif branch == 'master':
        commits = get_immediate_subdirectories(
            os.path.join(get_jet_directory() + '/.jet/'))
    else:
        commits = get_immediate_subdirectories(
            os.path.join(get_jet_directory() + '/.jet/branches/%s' % branch))
    try:
        commits.remove('branches')
    except ValueError:
        pass
    if number in commits:
        return True
    else:
        return False


def edit_commit_list(branch, commit_number, current_list):
    if branch == 'master':
        filename = os.path.join(get_jet_directory()
                                + '/.jet/%s/file_log.txt'
                                % commit_number)
    else:
        filename = os.path.join(get_jet_directory()
                                + '/.jet/branches/%s/%s/file_log.txt'
                                % (branch, commit_number))
    if commit_number == 0:
        raise AttributeError
    with open(filename, 'r') as myFile:
        edits = myFile.read().splitlines()
    for edit in edits:
        if edit.startswith('+'):
            current_list.append(edit[1:])
        elif edit.startswith('-'):
            try:
                current_list.remove(edit[1:])
            except ValueError:
                pass
        else:
            pass
    return current_list


def get_highest_commit(branch):
    if branch != 'master':
        directories = get_immediate_subdirectories(os.path.join(
            get_jet_directory() + '/.jet/branches/%s' % branch))
    else:
        directories = get_immediate_subdirectories(
            os.path.join(get_jet_directory() + '/.jet/'))
        try:
            directories.remove("branches")
        except ValueError:
            pass
    highest = 0
    for directory in directories:
        if directory > highest:
            highest = directory
    return "%s" % highest


def get_parent(branch):
    if branch == 'master':
        raise AttributeError
    filename = os.path.join(get_jet_directory()
                            + '/.jet/branches/%s/parent' % branch)
    with open(filename, 'r') as myFile:
        lines = myFile.read().splitlines()
    return lines[0]


def get_parent_commit(branch):
    if branch == 'master':
        raise AttributeError
    filename = os.path.join(get_jet_directory()
                            + '/.jet/branches/%s/parent' % branch)
    with open(filename, 'r') as myFile:
        lines = myFile.read().splitlines()
    return lines[1]


def get_file_list_at(branch, commit_number):
    if branch == 'master':
        filename = os.path.join(get_jet_directory() + '/.jet/0/file_log.txt')
    else:
        filename = os.path.join(get_jet_directory()
                                + '/.jet/branches/%s/0/file_log.txt' % branch)
    with open(filename, 'r') as myFile_:
        branch_file_list = myFile_.read().splitlines()

    if commit_number > 0:
        commit_int = int(commit_number)
        for i in range(1, commit_int + 1):
            branch_file_list = edit_commit_list(branch, i, branch_file_list)
    return branch_file_list


def revert(branch, commit_number):
    current_files = get_current_files(None)
    files_at_revert_point = get_file_list_at(branch, commit_number)
    files_to_delete = [x for x in current_files
                       if not x in files_at_revert_point]
    for current_filename_to_process in files_to_delete:
        os.remove(current_filename_to_process)
    for current_filename_to_process in files_at_revert_point:
        new_contents = get_file_at(branch, commit_number,
                                   current_filename_to_process)
        with open(current_filename_to_process, 'w') as myFile:
            for content in new_contents:
                myFile.write("%s\n" % content)

    filename = os.path.join(get_jet_directory() + '/.jet/branch')
    with open(filename, 'w') as current_filename_to_process:
        current_filename_to_process.write(branch)
    filename = os.path.join(get_jet_directory() + '/.jet/current_commit')
    with open(filename, 'w') as current_filename_to_process:
        current_filename_to_process.write(str(commit_number))


def get_branch():
    filename = os.path.join(get_jet_directory() + '/.jet/branch')
    with open(filename, 'r') as myFile:
        lines = myFile.read().splitlines()
    return lines[0]


def get_commit():
    filename = os.path.join(get_jet_directory() + '/.jet/current_commit')
    with open(filename, 'r') as myFile:
        lines = myFile.read().splitlines()
    return lines[0]


def get_joint_parent(branch_1, branch_2):
    mutual_branch = 'master'
    b1_branch_list = []
    while not branch_1 == 'master':
        b1_branch_list.append(branch_1)
        branch_1 = get_parent(branch_1)
    b2_branch_list = []
    while not branch_2 == 'master':
        b2_branch_list.append(branch_2)
        branch_2 = get_parent(branch_2)
    b1_branch_list.append('master')
    b2_branch_list.append('master')
    found = False
    for b1 in b1_branch_list:
        if found:
            continue
        for b2 in b2_branch_list:
            if b1 == b2:
                mutual_branch = b2
                found = True
                continue

    index = b2_branch_list.index(mutual_branch)
    index_of_child = index - 1
    try:
        mutual_commit = get_parent_commit(b2_branch_list[index_of_child])
    except IndexError:
        mutual_commit = 0

    return mutual_branch, mutual_commit


# This method takes in as parameter a branch name,
# and then merges it with the current branch.
# Will cause a merge conflict if it's mathematically
# impossible to decide what content should appear
def merge(branch_to_merge):
    # The parameters is merged with the current
    #  branch, so get the current branch
    current_branch = get_branch()
    # Get all the files currently in the repository
    current_files = get_current_files(None)
    # Get all the files in the branch to merge with
    other_files = get_file_list_at(branch_to_merge,
                                   get_highest_commit(branch_to_merge))

    # Get the parent branch of the two branches, ie - where did they diverge?
    # Also gets the commit number of the exact
    #  point where the two branches seperated.
    joint_parent_branch,\
        joint_parent_commit_number = get_joint_parent(current_branch,
                                                      branch_to_merge)
    # Can now use these to get the file list at this point in time
    parent_files = get_file_list_at(joint_parent_branch,
                                    joint_parent_commit_number)

    # Initialize empty arrays
    
    # Files to merge are ones that exist in both the new and other branch
    files_to_merge = []
    # Files to ask about are ones that only exist in
    # one of the branches, therefore ask if they should be kept.
    files_to_ask_about = []

    # Loop through each of the current files and
    # check if they're in the other file list
    for file_ in current_files:
        if file_ in other_files:
            # If they're in both, some kind of merge needs to take place
            files_to_merge.append(file_)
        else:
            # Otherwise - ask the user if they wish to keep the file.
            files_to_ask_about.append(file_)
            
    # Now loop through the other files and
    #  check if they're not in current files.
    # If they are, they'll already be in the merge list, so nothing needs doing
    files_to_ask_about += [x for x in other_files if x not in current_files]

    # Loop through all the files Jet is unsure about
    for f in files_to_ask_about:
        # Now ask the user if they wish to keep the file
        answer = ask(f)
        # If the answer is no...
        if not answer:
            # Just delete the file
            os.remove(f)
        else:
            # If the file isn't already saved locally...
            if f not in current_files:
                # Get the contents of the file
                file_contents = get_file_at(branch_to_merge,
                                            get_highest_commit
                                            (branch_to_merge),
                                            f)
                # If fetching the contents worked...
                if file_contents:
                    # ensure there is a directory to place the file into
                    make_directories(f, clone=False)
                    # Write them into the file, and save
                    with open(f, 'w') as myFile:
                        for line in file_contents:
                            myFile.write(line)

    # Now loop through all the files that need merging
    for f in files_to_merge:
        # Check to see if the file has a parent it diverged from
        if f in parent_files:
            # If it does, get the parent files contents
            parent_file = get_file_at(joint_parent_branch,
                                      joint_parent_commit_number,
                                      f)
        else:
            # Otherwise, use an empty array as the parents contents.
            parent_file = []

        # Get the contents of the file in it's current state
        file1 = get_file_at(current_branch,
                            get_highest_commit(current_branch),
                            f)
        # Get the contents of the file in it's other state
        file2 = get_file_at(branch_to_merge,
                            get_highest_commit(branch_to_merge),
                            f)
        # Merge the files! 
        merge_files(f, parent_file, file1, file2)


# Asks the user if they wish to keep a specific file or not
def ask(filename):
    # Get the response from the user
    response = raw_input("Would you like to keep the file: %s? (yes/no) "
                         % filename)
    # Also allow y as a response
    if response == "yes" or response == "y" or response == "Yes":
        # True means keep the file
        return True
    else:
        return False


# This method takes a file, containing merge conflicts, and optimizes them to 
# attempt to have as few separate conflicts as possible
def optimize_conflicts(_file_):
    optimized = False
    # Set variables to show the start,
    #  middle and end of a conflict declaration.
    # Conflicts are formed:
    #     Start of file
    #     @@@@@@@@@@HEAD@@@@@@@@@@
    #     File 1's contents
    #     @@@@@@@@@@SEPARATOR@@@@@@@@@@
    #     File 2's contents
    #     @@@@@@@@@@END@@@@@@@@@@
    #     Rest of file
    start = '@@@@@@@@@@HEAD@@@@@@@@@@'
    separator = '@@@@@@@@@@SEPARATOR@@@@@@@@@@'
    end = '@@@@@@@@@@END@@@@@@@@@@'
    optimized_file = _file_
    # Loop through each line in the file, using i as a pointer / counter
    for i in range(0, len(_file_)):
        try:
            # If the line is an end of conflict declaration
            if _file_[i] == end:
                # And the next line is a start of conflict declaration
                if _file_[i+1] == start:
                    # Then the file can be optimized! 
                    optimized = True
                    end_of_set = None
                    # Loop through until the end of the
                    # file to find the end of that conflict
                    # Set the end_of_set variable to
                    # the index of end of conflict
                    for j in range(i+1, len(_file_)):
                        if _file_[j] == end:
                            end_of_set = j
                            # Once found, exit for loop
                            break
                    start_of_set = None
                    # Loop from the end of conflict marker until
                    # the start of that conflict is found
                    # Set the start_of_set variable to the ends
                    # of start of that conflict
                    for k in range(i-1, -1, -1):
                        if _file_[k] == start:
                            start_of_set = k
                            break
                    # If neither could be found, cannot optimize.
                    if start_of_set is None and end_of_set is None:
                        continue
                    # Empty arrays that will hold the contents of the conflict
                    first_contents = []
                    second_contents = []
                    # Loop through from the start of first conflict,
                    #  until the end of that conflict to get the contents
                    for y in range(start_of_set + 1, i):
                        if _file_[y] == separator:
                            # After separator is found,
                            #  it's then the other files contents
                            for z in range(y+1, i):
                                second_contents.append(_file_[z])
                            break
                        # Add to first contents array
                        first_contents.append(_file_[y])
                    # Do the same for the second conflict being optimized. 
                    for y in range(i+2, end_of_set):
                        # Loop through the second conflict.
                        if _file_[y] == separator:
                            # After separator is found, it's then
                            # the other files contents
                            for z in range(y+1, end_of_set):
                                second_contents.append(_file_[z])
                            break
                        # Add to first contents array
                        first_contents.append(_file_[y])
                    # Optimized file is then adjusted to take
                    #  into account the new contents, with one less conflict
                    optimized_file = _file_[:start_of_set] +\
                        [start] +\
                        first_contents +\
                        [separator] +\
                        second_contents +\
                        [end] +\
                        _file_[end_of_set+1:]
                    # Stop trying to optimize and restart the process.
                    break
        except IndexError:
            continue
    # If it was optimized, try again! 
    if optimized:
        optimized_file = optimize_conflicts(optimized_file)
    # Otherwise just return the file
    return optimized_file


# This function takes a filename,
# it's contents in the parent, current and other branch
# It then compares the contents, and if it's possible
# to figure out what result to give, then do it
# Otherwise, merge conflict.
def fix_file(filename, parent, file1, file2, test=False):
    # New file starts as blank
    _file_ = []
    # Hopeful - assume no merge conflicts!!! 
    conflict = False
    # Initialize all pointers
    parent_pointer = 0
    file1_pointer = 0
    file2_pointer = 0
    # Length of all 3 files combined
    total_length = max(len(parent), len(file1), len(file2))
    # To prevent any errors, extend the length
    # of each of the files to the total length
    for i in range(len(parent), total_length):
        parent.append("")
    for i in range(len(file1), total_length):
        file1.append("")
    for i in range(len(file2), total_length):
        file2.append("")
    # Now all the files are the exact same size
    while parent_pointer < total_length:
        # if two versions are the same
        if file2[file2_pointer] == file1[file1_pointer]:
            # append the line to the final file
            _file_.append(file1[file1_pointer])
            # increment all pointers
            parent_pointer += 1
            file1_pointer += 1
            file2_pointer += 1
        # if file2 was changed, but not file1
        elif file1[file1_pointer] == parent[parent_pointer] and \
                not file2[file2_pointer] == parent[parent_pointer]:
            # append the line to the final file
            _file_.append(file2[file2_pointer])
            # increment all pointers
            parent_pointer += 1
            file1_pointer += 1
            file2_pointer += 1
        # if file1 was changed, but not file2
        elif file2[file2_pointer] == parent[parent_pointer] and \
                not file1[file1_pointer] == parent[parent_pointer]:
            # append the line to the final file
            _file_.append(file1[file1_pointer])
            # increment all pointers
            parent_pointer += 1
            file1_pointer += 1
            file2_pointer += 1
        else:
            # MERGE CONFLICT has happened
            _file_.append('@@@@@@@@@@HEAD@@@@@@@@@@')
            # File1s contents
            _file_.append(file1[file1_pointer])
            _file_.append('@@@@@@@@@@SEPARATOR@@@@@@@@@@')
            # File2s contents
            _file_.append(file2[file2_pointer])
            _file_.append('@@@@@@@@@@END@@@@@@@@@@')
            # conflict has happened, so will need to mark the file
            conflict = True
            # keep going! so increment pointers
            parent_pointer += 1
            file1_pointer += 1
            file2_pointer += 1
    # Only mark the file as a conflict if not a unit test
    if conflict and not test:
        add_conflict(filename)

    # Remove blank lines from the end of the file
    count = 0
    # reversed so start from end
    for f in reversed(_file_):
        # When content has been reached, stop
        if not f == '':
            break
        else:
            count += 1
        
    if count > 0:
        # Delete all the blank lines
        del _file_[-count:]
    # Optimize conflicts and return to user!
    finished = optimize_conflicts(_file_)
    if test:
        for i in range(0, len(finished)):
            if finished[i] == '@@@@@@@@@@HEAD@@@@@@@@@@':
                finished[i] = '# @@@@@@@@@@HEAD@@@@@@@@@@'
            if finished[i] == '@@@@@@@@@@SEPARATOR@@@@@@@@@@':
                finished[i] = '# @@@@@@@@@@SEPARATOR@@@@@@@@@@'
            if finished[i] == '@@@@@@@@@@END@@@@@@@@@@':
                finished[i] = '# @@@@@@@@@@END@@@@@@@@@@'
        return finished
    else:
        return finished


# This method takes as input a filename, the contents of it at
# the parents(if exists), the current branch
# and the other branch being merged - and then gives the result
#  saved into the file.
def merge_files(filename, parent, file1, file2):
    # base case
    if file1 == file2:
        new_file = file1
    else:
        # merging is required
        try:
            new_file = fix_file(filename, parent, file1, file2)
        except IndexError:
            # error has happened. Apply worst case scenario.
            new_file = \
                ['@@@@@@@@@@HEAD@@@@@@@@@@\n'] \
                + file1 \
                + ['\n@@@@@@@@@@SEPARATOR@@@@@@@@@@\n'] \
                + file2 \
                + ['\n@@@@@@@@@@END@@@@@@@@@@']
            add_conflict(filename)

    # Write the new files contents
    with open(filename, 'w') as myFile:
        for line in new_file:
            myFile.write('%s\n' % line)


# Returns a boolean of true or false on if any files have outstanding conflicts
def is_conflicts():
    return not len(get_conflicts()) == 0


def get_conflicts():
    file_ = os.path.join(get_branch_location() + 'conflicts')
    try:
        with open(file_, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        lines = []
    return lines


def add_conflict(filename):
    conflicts = get_conflicts()
    if filename not in conflicts:
        conflicts.append(filename)

    file_ = os.path.join(get_branch_location() + 'conflicts')

    print (BColors.RED + "Merge conflict for"
                         " file %s" % filename + BColors.ENDC)

    with open(file_, 'w') as myFile:
        for line in conflicts:
            myFile.write('%s\n' % line)


def resolve_conflict(filename):
    conflicts = get_conflicts()
    if filename in conflicts:
        conflicts.remove(filename)
    else:
        return -1

    file_ = os.path.join(get_branch_location() + 'conflicts')

    with open(file_, 'w') as myFile:
        for line in conflicts:
            myFile.write('%s\n' % line)

    return len(conflicts)


def filter_one_file_by_ignore(filename):
    try:
        name_of_jet_ignore = os.path.join(get_jet_directory() + '/.jet_ignore')
        with open(name_of_jet_ignore, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return filter_file_by_ignore(filename, [])
    return filter_file_by_ignore(filename, lines)


# True for passed, false for ignore
def filter_file_by_ignore(filename, lines):
    for line in lines:
        if line.startswith('*') and line.endswith('*'):
            if line[1:-1] in filename:
                return False
        if line.startswith('*'):
            if filename.endswith(line[1:]):
                return False
        if line.endswith('*'):
            if filename.startswith(line[:1]):
                return False
        if line == filename:
            return False
        cwd = os.getcwd()
        relative_filename = filename[len(cwd):]
        if relative_filename.startswith('/'):
            relative_filename = relative_filename[1:]
        if relative_filename.startswith(line):
            return False
    if filename.endswith("~"):
        return False

    # if none of it matches
    return True


def filter_files_by_ignore(filenames):
    try:
        name_of_jet_ignore = os.path.join(get_jet_directory() + '/.jet_ignore')
        with open(name_of_jet_ignore, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return [x for x in filenames if (filter_file_by_ignore(x, []))]
    return [x for x in filenames if (filter_file_by_ignore(x, lines))]


def relative(filename, cwd):
    if cwd in filename:
        to_return = filename[len(cwd):]
        if to_return.startswith('/'):
            return to_return[1:]
        else:
            return to_return
    else:
        h, t = os.path.split(filename)
        count = 0
        if h == '':
            h = '~J/E\T'
            count = len(cwd.split('/')) - 2
        if h in cwd:
            return '../%s' % t
        head = filename
        to_append = []

        while head not in cwd:
            head, tail = os.path.split(head)
            count += 1
            to_append.append(tail)
            if head == '':
                break
        back_slashes = []
        count -= 1
        while count > 0:
            back_slashes.append('../')
            count -= 1
        to_append.reverse()
        relative_name = "%s%s" % (''.join(back_slashes),
                                  '/'.join(to_append))
        return relative_name


def get_user_id():
    filename = os.path.join(get_jet_directory() + '/.jet/username')
    try:
        with open(filename, 'r') as file_:
                    lines = file_.read().splitlines()
        user_id = lines[1]
    except IOError:
        user_id = None
    except IndexError:
        user_id = None
    return user_id


def get_repo_id():
    filename = os.path.join(get_jet_directory() + '/.jet/repo_id')
    try:
        with open(filename, 'r') as file_:
            lines = file_.read().splitlines()
        repo_id = lines[0]
    except IOError:
        repo_id = None
    return repo_id


def is_setup():
    return get_user_id() and get_repo_id()


def make_directories(filename, clone):
    if clone:
        jet_directory = os.getcwd()
    else:
        jet_directory = get_jet_directory()
    stripped_filename = filename[len(jet_directory):]
    if stripped_filename.startswith('/'):
        stripped_filename = stripped_filename[1:]
    fname = os.path.basename(stripped_filename)
    folders = stripped_filename[:-len(fname)]
    try:
        os.makedirs(folders)
    except OSError:
        pass


def get_last_server_pull(branch):
    filename = os.path.join(get_branch_location_param(branch) + 'last_pull')
    try:
        with open(filename, 'r') as file_:
            lines = file_.read().splitlines()
        last_pull = int(lines[0])
    except IOError:
        last_pull = -1
    return last_pull


def save_last_pull(branch, new_number):
    filename = os.path.join(get_branch_location_param(branch) + 'last_pull')
    with open(filename, 'w') as file_:
        file_.write(str(new_number))


def get_last_update(branch):
    filename = os.path.join(get_branch_location_param(branch) + 'last_update')
    try:
        with open(filename, 'r') as file_:
            lines = file_.read().splitlines()
        commit_number = int(lines[0])
    except IOError:
        commit_number = 0
    return branch, commit_number


def add_update(branch, commit):
    filename = os.path.join(get_branch_location_param(branch) + 'last_update')
    with open(filename, 'w') as file_:
        file_.write(str(commit))
