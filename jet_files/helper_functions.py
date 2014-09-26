import os
from os import walk
import hashlib


def get_jet_directory():
    directory = os.getcwd()
    parent = os.path.abspath(os.path.join(directory, os.pardir))
    jet_directory = ""
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


def get_immediate_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def get_current_files():
    file_list = []
    for (dirpath, dirnames, filenames) in walk(get_jet_directory()):
        for filename in filenames:
            file_list.append(os.path.join(dirpath, filename))

    jet_files_stored = []
    for (path, dirnames, filenames) in walk(os.path.join
                                           (get_jet_directory() + '/.jet/')):
        for filename in filenames:
            jet_files_stored.append(os.path.join(path, filename))

    current_files = []
    for file_to_check in file_list:
        if file_to_check not in jet_files_stored and not\
                file_to_check.endswith("~"):
            current_files.append(file_to_check)
    return current_files


def get_new_commit_number():
    commits = get_immediate_subdirectories(os.path.join(get_jet_directory() +
                                                        '/.jet/'))
    latest = commits[-1]
    int_latest = int(latest)
    new_commit_number = int_latest + 1
    return new_commit_number


def get_stored_files_and_hashes():
    #~J/E\T is the keyword separating files
    filename = os.path.join(get_jet_directory() + '/.jet/latest_saved_files')
    with open(filename, 'r') as myFile:
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
        filename = os.path.join(get_jet_directory() + '/.jet/changeset.txt')
        with open(filename, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return []
    new_files = []
    for line in lines:
        if line.startswith('+'):
            new_files.append(line[1:])
    return new_files


def get_deleted_files_in_changeset():
    try:
        filename = os.path.join(get_jet_directory() + '/.jet/changeset.txt')
        with open(filename, 'r') as myFile:
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
        filename = os.path.join(get_jet_directory() + '/.jet/changeset.txt')
        with open(filename, 'r') as myFile:
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
    return not get_jet_directory() == ""


def checksum_md5(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''): 
            md5.update(chunk)
    return md5.digest()


def get_changed_files():
    current_files = get_current_files()
    changed_files = []
    for file_to_compare in current_files:
        if not checksum_md5(file_to_compare) ==\
                get_stored_hash(file_to_compare):
            changed_files.append(file_to_compare)
    return changed_files


def get_change_description(filename):
    commit_number = get_new_commit_number() - 1
    previous_file = get_file_at(commit_number, filename)

    difference = diff(previous_file, filename)
    if not difference:
        return "Jet is sorry, but there was an error in processing the" \
               " changes for this file"
    else:
        return difference


def diff(file1, file2):
    try:
        with open(file1, 'r') as file_:
            old_lines = file_.read().splitlines()
        with open(file2, 'r') as file_:
            current_lines = file_.read().splitlines()
        #print "Before"
        #print old_lines
        #print "After"
        #print current_lines
    except IOError:
        return "Jet is sorry, but there was an error in processing the" \
               " changes for this file"
    description = ""
    line_number = -1
    count = -1
    old_count = -1
    while old_count < len(old_lines):
        old_count += 1
        count += 1
        line_number += 1
        try:
            line = old_lines[old_count]
        except IndexError:
            break
        try:
            current_lines[count]
        except IndexError:
            description += ("(" + str(line_number) + ") " +
                            "- " +
                            line +
                            "\n")
            continue
        #print "Comparing %s and %s" % (line, current_lines[count])
        #print "Old count is %s, count is %s" % (old_count, count)

        if not current_lines[count] == line:
            if line == "":
                description += ("(" + str(line_number) + ") " +
                                "- blank line\n")
                count -= 1
            else:
                if current_lines[count] == "":
                    description += ("(" + str(line_number) + ") " +
                                    "+ blank line\n")
                    old_count -= 1
                else:
                    description += ("(" + str(line_number) + ") " +
                                    "~ " + current_lines[count] + "\n")

    while count <= len(current_lines) - 1:
        if current_lines[count] == "":
            description += ("(" + str(line_number) + ") " +
                            "+ blank line\n")
        else:
            description += ("(" + str(line_number) + ") " +
                            "+ " +
                            current_lines[count] +
                            "\n")
        line_number += 1
        count += 1

    description_to_return = description[:-1]
    if description_to_return == "":
        return "No changes found"
    else:
        return description_to_return


def get_file_at(commit_number, filename):
    return os.path.join(get_jet_directory() + '/.jet/temp')


def reform_file(filename, diff):
    return os.path.join(get_jet_directory() + '/.jet/temp')