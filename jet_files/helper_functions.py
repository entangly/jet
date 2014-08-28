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
    for (dirpath, dirnames, filenames) in walk(os.getcwd()):
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
    commits = get_immediate_subdirectories(os.path.join(os.getcwd() +
                                                        '/.jet/'))
    latest = commits[-1]
    int_latest = int(latest)
    new_commit_number = int_latest + 1
    return new_commit_number


def get_stored_files_and_hashes():
    #~J/E\T is the keyword separating files
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
    print filename
    return "File was changed"