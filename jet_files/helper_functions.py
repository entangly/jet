import os
from os import walk
import hashlib
import subprocess


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


def get_branch_location():
    branch = get_branch()
    if branch == 'master':
        return os.path.join(get_jet_directory() + '/.jet/')
    else:
        return os.path.join(get_jet_directory() + '/.jet/branches/%s/'
                            % branch)


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
    commits = get_immediate_subdirectories(get_branch_location())
    try:
        commits.remove('branches')
    except ValueError:
        pass
    biggest = 0
    for commit in commits:
        try:
            commit_num = int(commit)
            if commit_num > biggest:
                biggest = commit_num
        except ValueError:
            pass
    int_latest = int(biggest)
    new_commit_number = int_latest + 1
    return new_commit_number


def get_stored_files_and_hashes():
    #~J/E\T is the keyword separating files
    filename = os.path.join(get_branch_location() + 'latest_saved_files')
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
        filename = os.path.join(get_branch_location() + 'changeset.txt')
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
        filename = os.path.join(get_branch_location() + 'changeset.txt')
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
        filename = os.path.join(get_branch_location() + 'changeset.txt')
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
    previous_file = get_file_at(get_branch(), commit_number, filename)
    if previous_file is None:
        return "File was added at this point"
    difference = diff(previous_file, filename)
    if not difference:
        return "Jet is sorry, but there was an error in processing the" \
               " changes for this file"
    else:
        return difference


def diff(file1, file2):
    try:
        if type(file1) == list:
            old_lines = file1
        else:
            with open(file1, 'r') as file_:
                old_lines = file_.read().splitlines()
        if type(file2) == list:
            current_lines = file2
        else:
            with open(file2, 'r') as file_:
                current_lines = file_.read().splitlines()
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


def get_file_change_number(branch, commit_number, filename):
    if not branch == 'master':
        file_list_file = os.path.join(get_jet_directory() +
                                      '/.jet/branches/%s/%s/file_log.txt'
                                      % (branch, commit_number))
    else:
        file_list_file = os.path.join(get_jet_directory() +
                                      '/.jet/%s/file_log.txt' % commit_number)
    with open(file_list_file, 'r') as myFile:
        file_list = myFile.read().splitlines()
    change_number = 0
    for file_ in file_list:
        if file_ == filename or file_[1:] == filename:
            return change_number
        else:
            change_number += 1
    return None


def get_last_complete_file(branch, filename):
    change_number = get_file_change_number(branch, 0, filename)
    if change_number is None:
        return None, None
    name_of_file = os.path.basename(filename)
    if not branch == 'master':
        modded_filename = os.path.join(get_jet_directory()
                                       + '/.jet/branches/%s/0/%s/%s'
                                       % (branch, change_number, name_of_file))
    else:
        modded_filename = os.path.join(get_jet_directory() + '/.jet/0/%s/%s'
                                       % (change_number, name_of_file))
    with open(modded_filename, 'r') as myFile:
            current_file = myFile.read().splitlines()
    commit_number = 0
    return current_file, commit_number


def get_diff_at(branch, commit_number, filename):
    change_num = get_file_change_number(branch, commit_number, filename)
    if not branch == 'master':
        modded_filename = os.path.join(get_jet_directory()
                                       + '/.jet/branches/%s/%s/%s/changes.txt'
                                       % (branch, commit_number, change_num))
    else:
        modded_filename = os.path.join(get_jet_directory()
                                       + '/jet/%s/%s/changes.txt'
                                       % (commit_number, change_num))
    with open(modded_filename, 'r') as myFile:
        difference = myFile.read().splitlines()
    return difference


def get_file_at(branch, commit_number, filename):
    last_complete, last_full_commit = get_last_complete_file(branch, filename)
    if last_complete is None:
        return None
    commits_to_add = []
    commit = last_full_commit + 1
    if commit_number == '0':
        return last_complete
    while commit < commit_number:
        commits_to_add.append(commit)
        commit += 1

    current_file = last_complete
    for c in commits_to_add:
        current_file = reform_file(current_file, get_diff_at(branch,
                                                             c,
                                                             filename))
        print current_file

    return current_file


def reform_file(_file_, diff_list):
    if type(_file_) == list:
        lines = _file_
    else:
        with open(_file_, 'r') as file_:
            lines = file_.read().splitlines()
    if diff_list[0] == 'No changes found':
        return lines
    for d in diff_list:
        index = d.index(' ')
        line_number_list = d[1:index-1]
        line_number = ''
        for number in line_number_list:
            line_number += number
        count = int(line_number)
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
    try:
        return_code = subprocess.call("python %s" % filename, shell=True)
    except Exception:
        return False
    if return_code == 0:
        return True
    else:
        return False


def is_valid_commit_number(number, branch):
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
        filename = os.path.join(get_jet_directory() + '/.jet/%s')
    else:
        filename = os.path.join(get_jet_directory() + '/.jet/branches')
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
    highest = 0
    for directory in directories:
        if directory > highest:
            highest = directory
    return highest


def get_parent(branch):
    if branch == 'master':
        raise AttributeError
    filename = os.path.join(get_jet_directory()
                            + '/.jet/branches/%s/parent' % branch)
    with open(filename, 'r') as myFile:
        lines = myFile.read().splitlines()
    return lines[0]


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
    current_files = get_current_files()
    files_at_revert_point = get_file_list_at(branch, commit_number)
    files_to_delete = [x for x in current_files
                       if not x in files_at_revert_point]
    for file_ in files_to_delete:
        os.remove(file_)
    for file_ in files_at_revert_point:
        new_contents = get_file_at(branch, commit_number, file_)
        with open(file_, 'w') as myFile:
            for content in new_contents:
                myFile.write(content)

    filename = '.jet/branch'
    with open(filename, 'w') as file_:
        file_.write(branch)
    print "Revert finished. You are now at the state of commit number %s " \
          "in branch %s" % (commit_number, branch)


def get_branch():
    filename = os.path.join(get_jet_directory() + '/.jet/branch')
    with open(filename, 'r') as myFile:
        lines = myFile.read().splitlines()
    return lines[0]