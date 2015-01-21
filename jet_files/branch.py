import os
from shutil import copyfile, rmtree
import helper_functions as hf
import sys


def branch(branch_name):
    filename = os.path.join(hf.get_jet_directory() + '/.jet/changeset.txt')
    changed_files = False
    if os.path.isfile(filename):
        changed_files = True
    if len(hf.get_changed_files()) > 0:
        changed_files = True
    if changed_files:
        print "You can't branch until you commit...."
        return
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path) or branch_name == "master":
        if os.path.exists(os.path.join(branches_path + branch_name)):
            print "Already a branch with that name... please try another!"
            return
        else:
            os.mkdir(os.path.join(branches_path + branch_name))
    else:
        os.mkdir(os.path.join(hf.get_jet_directory() + '/.jet/branches/'))
        os.mkdir(os.path.join(branches_path + branch_name))

    f = []
    filenames_list = []
    for (dirpath, dirnames, filenames) in os.walk(hf.get_jet_directory()):
        for filename in filenames:
            if hf.filter_one_file_by_ignore(filename):
                if not '.jet' in dirpath:
                    filenames_list.append(filename)
                    f.append(os.path.join(dirpath, filename))
    file_name = os.path.join(hf.get_jet_directory()
                             + '/.jet/branches/%s/latest_saved_files'
                             % branch_name)
    with open(file_name, 'w') as file_:
        for file_to_add in f:
            file_.write(file_to_add + "~J/ET")
            file_.write(hf.checksum_md5(file_to_add) + "~J/ET")
    os.mkdir('.jet/branches/%s/0/' % branch_name)
    file_name = os.path.join(hf.get_jet_directory()
                             + '/.jet/branches/%s/0/file_log.txt'
                             % branch_name)
    with open(file_name, 'w') as file_:
        for file_to_add in f:
            file_.write(file_to_add + "\n")

    count = 0
    for file_to_add in f:
        folder = os.path.join(hf.get_jet_directory() +
                              '/.jet/branches/%s/%s/%s' % (branch_name,
                                                           0,
                                                           count))
        os.mkdir(folder)
        filename = os.path.join(hf.get_jet_directory() +
                                '/.jet/branches/%s/%s/%s/filename.txt'
                                % (branch_name, 0, count))
        with open(filename, 'w') as myFile:
                myFile.write(file_to_add)
        filename = filenames_list[count]
        copyfile(file_to_add, os.path.join(hf.get_jet_directory()
                                           + '/.jet/branches/%s/0/%s/%s'
                                           % (branch_name,
                                              count,
                                              filename)))
        count += 1

    print "Branch %s made" % branch_name
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/branches/%s/parent' % branch_name)
    old_branch = hf.get_branch()
    old_commit = hf.get_commit()
    with open(filename, 'w') as file_:
        file_.write(old_branch)
        file_.write('\n')
        file_.write(old_commit)
    filename = os.path.join(hf.get_jet_directory() + '/.jet/branch')
    with open(filename, 'w') as file_:
        file_.write(branch_name)
    filename = os.path.join(hf.get_jet_directory() + '/.jet/current_commit')
    with open(filename, 'w') as file_:
        file_.write("0")
    print "You are now working in branch %s" % branch_name


def run():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 3:
        print "Please form branch commands by typing" \
              " $jet branch <branch_name>"
        return
    branch_name = sys.argv[2]
    branch(branch_name)


def switch():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(sys.argv) != 3:
        print "Please form your switch commands $jet switch <branch_name>"
        return
    filename = os.path.join(hf.get_jet_directory() + '/.jet/changeset.txt')

    # Checks for any changed files, as you must have committed first!!!
    changed_files = False
    if os.path.isfile(filename):
        changed_files = True
    if len(hf.get_changed_files()) > 0:
        changed_files = True
    if changed_files:
        print "You can't switch branch until you commit...."
        return

    if sys.argv[2] == 'master':
        filename = '.jet/branch'
        with open(filename, 'w') as file_:
            file_.write(sys.argv[2])
        hf.revert(sys.argv[2], hf.get_highest_commit(sys.argv[2]))
        filename = os.path.join(hf.get_branch_location()
                                + 'latest_saved_files')
        os.remove(filename)
        with open(filename, 'w') as file_:
            for file_to_add in hf.get_current_files():
                file_.write(file_to_add + "~J/ET")
                file_.write(hf.checksum_md5(file_to_add) + "~J/ET")
        print "Successfully switched to branch %s" % sys.argv[2]
        return
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        if os.path.exists(os.path.join(branches_path + sys.argv[2])):
            filename = '.jet/branch'
            with open(filename, 'w') as file_:
                file_.write(sys.argv[2])
            hf.revert(sys.argv[2], hf.get_highest_commit(sys.argv[2]))
            filename = os.path.join(hf.get_branch_location()
                                    + 'latest_saved_files')
            os.remove(filename)
            with open(filename, 'w') as file_:
                for file_to_add in hf.get_current_files():
                    file_.write(file_to_add + "~J/ET")
                    file_.write(hf.checksum_md5(file_to_add) + "~J/ET")
            print "Successfully switched to branch %s" % sys.argv[2]
        else:
            print "Invalid branch name"
    else:
        print "Invalid branch name"


def display():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "Branch name (parent)"
    print "Master(root)"
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        branches = hf.get_immediate_subdirectories(branches_path)
        for b in branches:
            print "%s (%s)" % (b, hf.get_parent(b))

    print "You are currently on branch %s" % hf.get_branch()


def delete_branch():
    if len(sys.argv) != 3:
        print "Please form your switch commands $jet switch <branch_name>"
        return
    branches_path = os.path.join(hf.get_jet_directory() + '/.jet/branches/')
    if os.path.exists(branches_path):
        if not os.path.exists(os.path.join(branches_path + sys.argv[2])):
            print "Invalid branch name, please try again."
            return
    delete(sys.argv[2])


def delete(branch_name):
    directory = os.path.join(hf.get_jet_directory()
                             + '/.jet/branches/%s/' % branch_name)
    rmtree(directory)