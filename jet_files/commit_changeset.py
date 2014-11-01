from shutil import copyfile
import helper_functions as hf
import sys
import os


def commit_changeset():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if not hf.logged_in():
        print "You must login before commiting! To do this type:" \
              " $jet login <username>"
        return
    hook = hf.get_commit_hook()
    if hook:
        result = hf.run_hook(hook)
        if result:
            print "Hook passed."
        else:
            print "Hook Failed. Not commiting"
            return
    if len(sys.argv) != 4 or sys.argv[2] != "-m":
        print "Commit commands need to be formed by typing:" \
              " $jet commit -m \"Your message here\""
    else:
        commit(sys.argv[3])


def commit(message):
    filename = os.path.join(hf.get_branch_location() + 'changeset.txt')
    if os.path.isfile(filename):
        new_files_in_changeset = hf.get_new_files_in_changeset()
        deleted_files_in_changeset = hf.get_deleted_files_in_changeset()
        changed_files_in_changeset = hf.get_changed_files_in_changeset()
        new_commit_number = hf.get_new_commit_number()
        folder = os.path.join(hf.get_branch_location() +
                              '/%s/' % new_commit_number)
        os.mkdir(folder)
        counter = 0
        filename = os.path.join(hf.get_branch_location()
                                + '/%s/file_log.txt'
                                % new_commit_number)
        with open(filename, 'w')\
                as file_:
            for file_to_add in new_files_in_changeset:
                file_.write("+" + file_to_add + "\n")
                #counter += 1
            for file_to_add in deleted_files_in_changeset:
                file_.write("-" + file_to_add + "\n")
                #counter += 1
            for file_to_add in changed_files_in_changeset:
                file_.write("~" + file_to_add + "\n")

        filename = os.path.join(hf.get_branch_location() + '/%s/info'
                                % new_commit_number)
        with open(filename, 'w') as file_:
            file_.write(hf.get_username() + '\n')
            file_.write(message)
        filename = os.path.join(hf.get_jet_directory() + '/.jet/current_commit')
        with open(filename, 'w') as file_:
            file_.write(str(new_commit_number))

        for file_ in changed_files_in_changeset:
            folder = os.path.join(hf.get_branch_location()
                                  + '/%s/%s' % (new_commit_number,
                                                counter))
            os.mkdir(folder)
            filename = os.path.join(hf.get_branch_location()
                                    + '/%s/%s/filename.txt'
                                    % (new_commit_number, counter))
            with open(filename, 'w') as myFile:
                myFile.write(file_)
            filename = os.path.join(hf.get_branch_location()
                                    + '/%s/%s/changes.txt'
                                    % (new_commit_number, counter))
            description = hf.get_change_description(file_)
            if description:
                with open(filename, 'w') as myFile:
                    myFile.write(description)
            else:
                copyfile(file_, filename)
            counter += 1

        filename = os.path.join(hf.get_branch_location()
                                + 'changeset.txt')
        os.remove(filename)

        lines = hf.get_stored_files()
        lines.extend(new_files_in_changeset)
        to_keep = []
        for line in lines:
            if line not in deleted_files_in_changeset:
                to_keep.append(line)
        filename = os.path.join(hf.get_branch_location()
                                + 'latest_saved_files')
        os.remove(filename)
        with open(filename, 'w') as file_:
            for file_to_add in to_keep:
                file_.write(file_to_add + "~J/ET")
                file_.write(hf.checksum_md5(file_to_add) + "~J/ET")
        print "Commiting"
    else:
        print "Please add files to commit using jet add before commiting!"


def run():
    commit_changeset()