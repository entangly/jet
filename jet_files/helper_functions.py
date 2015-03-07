import os
from os import walk
import hashlib
import subprocess


class BColors:
    def __init__(self):
        pass

    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


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


def get_branch_location_param(branch):
    if branch == 'master':
        return os.path.join(get_jet_directory() + '/.jet/')
    else:
        return os.path.join(get_jet_directory() + '/.jet/branches/%s/'
                            % branch)


def get_immediate_subdirectories(directory):
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]


def get_current_files(jet_directory):
    if jet_directory is None:
        jet_directory = get_jet_directory()
    file_list = []
    for (dirpath, dirnames, filenames) in walk(jet_directory):
        if '.jet' in dirpath:
            continue
        for filename in filenames:
            file_list.append(os.path.join(dirpath, filename))

    return filter_files_by_ignore(file_list)


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
    # TODO - change this to split by lines
    filename = os.path.join(get_branch_location() + 'latest_saved_files')
    with open(filename, 'r') as myFile:
        data = myFile.read().splitlines()
    return data
    # word = []
    # lines = []
    # code = []
    # for char in data:
    #     if char == "~" and len(code) == 0:
    #         code.append(char)
    #     elif char == "J" and len(code) == 1:
    #         code.append(char)
    #     elif char == "/" and len(code) == 2:
    #         code.append(char)
    #     elif char == "E" and len(code) == 3:
    #         code.append(char)
    #     elif char == "T" and len(code) == 4:
    #         code.append(char)
    #         new_line = ''.join(word)
    #         lines.append(new_line)
    #         word = []
    #         code = []
    #     else:
    #         word.extend(code)
    #         if not char == "~":
    #             code = []
    #             word.append(char)
    # if len(word) > 0:
    #     lines.append(''.join(word[:-5]))
    # return lines


def get_stored_files(lines):
    if lines is None:
        lines = get_stored_files_and_hashes()
    return lines[::2]


def get_stored_hash(filename, stored_files_and_hashes):
    if not stored_files_and_hashes:
        stored_files_and_hashes = get_stored_files_and_hashes()
    return_next = False
    for line in stored_files_and_hashes:
        if return_next:
            return line
        if line == filename:
            return_next = True
    return False


def get_new_files(current_files, stored_files):
    if current_files is None:
        current_files = get_current_files(None)
    if stored_files is None:
        stored_files = get_stored_files(None)
    return [x for x in current_files if x not in stored_files]


def get_files_in_changeset(branch_location):
    if branch_location is None:
        branch_location = get_branch_location()
    try:
        filename = os.path.join(branch_location + 'changeset.txt')
        with open(filename, 'r') as myFile:
            lines = myFile.read().splitlines()
    except IOError:
        return []
    return lines


def get_new_files_in_changeset(lines):
    if lines is None:
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


def get_deleted_files_in_changeset(lines):
    if lines is None:
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


def get_changed_files_in_changeset(lines):
    if lines is None:
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


def already_initialized():
    return not get_jet_directory() == ""


def checksum_md5(filename):
    with open(filename, 'r') as f:
        contents = f.read()
    return hashlib.md5(contents).hexdigest()


def old_checksum_md5(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''): 
            md5.update(chunk)
    return md5.digest()


def get_changed_files(current_files, stored_files_and_hashes):
    if current_files is None:
        current_files = get_current_files(None)
    changed_files = []
    for file_to_compare in current_files:
        if not checksum_md5(file_to_compare) ==\
                get_stored_hash(file_to_compare, stored_files_and_hashes):
            changed_files.append(file_to_compare)
    return changed_files


def get_change_description(filename):
    commit_number = get_new_commit_number() - 2
    previous_file = get_file_at(get_branch(), commit_number, filename)
    if previous_file is None:
        return None
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
    for file_ in files_to_delete:
        os.remove(file_)
    for file_ in files_at_revert_point:
        new_contents = get_file_at(branch, commit_number, file_)
        with open(file_, 'w') as myFile:
            for content in new_contents:
                myFile.write("%s\n" % content)

    filename = os.path.join(get_jet_directory() + '/.jet/branch')
    with open(filename, 'w') as file_:
        file_.write(branch)
    filename = os.path.join(get_jet_directory() + '/.jet/current_commit')
    with open(filename, 'w') as file_:
        file_.write(str(commit_number))


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


def merge(branch_to_merge):
    current_branch = get_branch()
    current_files = get_current_files(None)
    other_files = get_file_list_at(branch_to_merge,
                                   get_highest_commit(branch_to_merge))

    joint_parent_branch,\
        joint_parent_commit_number = get_joint_parent(current_branch,
                                                      branch_to_merge)
    parent_files = get_file_list_at(joint_parent_branch,
                                    joint_parent_commit_number)

    files_to_merge = []
    files_to_ask_about = []

    for file_ in current_files:
        if file_ in other_files:
            files_to_merge.append(file_)
        else:
            files_to_ask_about.append(file_)
    files_to_ask_about += [x for x in other_files if x not in current_files]

    for f in files_to_ask_about:
        answer = ask(f)
        if not answer:
            os.remove(f)
        else:
            if f not in current_files:
                file_contents = get_file_at(branch_to_merge,
                                            get_highest_commit
                                            (branch_to_merge),
                                            f)
                if file_contents:
                    with open(f, 'w') as myFile:
                        for line in file_contents:
                            myFile.write(line)

    for f in files_to_merge:
        if f in parent_files:
            parent_file = get_file_at(joint_parent_branch,
                                      joint_parent_commit_number,
                                      f)
        else:
            parent_file = []

        file1 = get_file_at(current_branch,
                            get_highest_commit(current_branch),
                            f)
        file2 = get_file_at(branch_to_merge,
                            get_highest_commit(branch_to_merge),
                            f)
        merge_files(f, parent_file, file1, file2)


def ask(filename):
    response = raw_input("Would you like to keep the file: %s? (yes/no) "
                         % filename)

    if response == "yes" or response == "y" or response == "Yes":
        return True
    else:
        return False


def optimize_conflicts(_file_):
    optimized = False
    start = '@@@@@@@@@@HEAD@@@@@@@@@@'
    separator = '@@@@@@@@@@SEPARATOR@@@@@@@@@@'
    end = '@@@@@@@@@@END@@@@@@@@@@'
    optimized_file = _file_
    for i in range(0, len(_file_)):
        try:
            if _file_[i] == end:
                if _file_[i+1] == start:
                    optimized = True
                    end_of_set = None
                    for j in range(i+1, len(_file_)):
                        if _file_[j] == end:
                            end_of_set = j
                            break
                    start_of_set = None
                    for k in range(i-1, -1, -1):
                        if _file_[k] == start:
                            start_of_set = k
                            break
                    if start_of_set is None and end_of_set is None:
                        continue
                    first_contents = []
                    second_contents = []
                    for y in range(start_of_set + 1, i):
                        if _file_[y] == separator:
                            for z in range(y+1, i):
                                second_contents.append(_file_[z])
                            break
                        first_contents.append(_file_[y])
                    for y in range(i+2, end_of_set):
                        if _file_[y] == separator:
                            for z in range(y+1, end_of_set):
                                second_contents.append(_file_[z])
                            break
                        first_contents.append(_file_[y])
                    optimized_file = _file_[:start_of_set] +\
                        [start] +\
                        first_contents +\
                        [separator] +\
                        second_contents +\
                        [end] +\
                        _file_[end_of_set+1:]
                    break
        except IndexError:
            continue
    if optimized:
        optimized_file = optimize_conflicts(optimized_file)
    return optimized_file


def fix_file(filename, parent, file1, file2, test=False):
    _file_ = []
    conflict = False
    parent_pointer = 0
    file1_pointer = 0
    file2_pointer = 0
    total_length = max(len(parent), len(file1), len(file2))
    for i in range(len(parent), total_length):
        parent.append("")
    for i in range(len(file1), total_length):
        file1.append("")
    for i in range(len(file2), total_length):
        file2.append("")
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
            # increment all pointers - SHOULD I?!?!?
            parent_pointer += 1
            file1_pointer += 1
            file2_pointer += 1
        # if file1 was changed, but not file2
        elif file2[file2_pointer] == parent[parent_pointer] and \
                not file1[file1_pointer] == parent[parent_pointer]:
            # append the line to the final file
            _file_.append(file1[file1_pointer])
            # increment all pointers - SHOULD I?!?!?
            parent_pointer += 1
            file1_pointer += 1
            file2_pointer += 1
        else:
            _file_.append('@@@@@@@@@@HEAD@@@@@@@@@@')
            _file_.append(file1[file1_pointer])
            _file_.append('@@@@@@@@@@SEPARATOR@@@@@@@@@@')
            _file_.append(file2[file2_pointer])
            _file_.append('@@@@@@@@@@END@@@@@@@@@@')

            conflict = True
            parent_pointer += 1
            file1_pointer += 1
            file2_pointer += 1
    if conflict and not test:
        add_conflict(filename)

    count = 0
    for f in reversed(_file_):
        if not f == '':
            break
        else:
            count += 1
    if count > 0:
        del _file_[-count:]
    return optimize_conflicts(_file_)


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

    with open(filename, 'w') as myFile:
        for line in new_file:
            myFile.write('%s\n' % line)


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

    print BColors.RED + "Merge conflict for file %s" % filename + BColors.ENDC

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
            if filename.contains(line[1:-1]):
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
        if h in cwd:
            return '../%s' % t
        head = filename
        to_append = []
        count = 0
        while head not in cwd:
            head, tail = os.path.split(head)
            count += 1
            to_append.append(tail)
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