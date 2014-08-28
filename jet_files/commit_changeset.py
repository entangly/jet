from jet_files import helper_functions as hf
import sys
import os


def commit_changeset():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    #print sys.argv[2]
    #print sys.argv[3]
    if len(sys.argv) != 4 or sys.argv[2] != "-m":
        print "Commit commands need to be formed by typing:" \
              " $jet commit -m \"Your message here\""
    else:
        if os.path.isfile(os.path.join(os.getcwd() + '/.jet/changeset.txt')):
            new_files_in_changeset = hf.get_new_files_in_changeset()
            deleted_files_in_changeset = hf.get_deleted_files_in_changeset()
            changed_files_in_changeset = hf.get_changed_files_in_changeset()
            new_commit_number = hf.get_new_commit_number()
            os.mkdir('.jet/%s/' % new_commit_number)
            counter = 0
            with open('.jet/%s/file_log.txt' % new_commit_number, 'w')\
                    as file_:
                for file_to_add in new_files_in_changeset:
                    file_.write("+" + file_to_add + "\n")
                    counter += 1
                for file_to_add in deleted_files_in_changeset:
                    file_.write("-" + file_to_add + "\n")
                    counter += 1
                for file_to_add in changed_files_in_changeset:
                    file_.write("~" + file_to_add + "\n")

            for file_ in changed_files_in_changeset:
                os.mkdir('.jet/%s/%s' % (new_commit_number, counter))
                with open('.jet/%s/%s/changes.txt' % (new_commit_number,
                                                      counter), 'w') as myFile:
                    myFile.write(hf.get_change_description(file_))
                    counter += 1

            os.remove(os.path.join(os.getcwd() + '/.jet/changeset.txt'))

            lines = hf.get_stored_files()
            lines.extend(new_files_in_changeset)
            to_keep = []
            for line in lines:
                if line not in deleted_files_in_changeset:
                    to_keep.append(line)
            os.remove(os.path.join(os.getcwd() + '/.jet/latest_saved_files'))
            with open('.jet/latest_saved_files', 'w') as file_:
                for file_to_add in to_keep:
                    file_.write(file_to_add + "~J/ET")
                    file_.write(hf.checksum_md5(file_to_add) + "~J/ET")
            print "Commiting"
        else:
            print "Please add files to commit using jet add before commiting!"


def run():
    commit_changeset()