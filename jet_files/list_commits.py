from jet_files import helper_functions as hf
import sys
import os


def list_commits():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    try:
        commit_number = sys.argv[2]
        if commit_number == "0":
            print "Initial commit"
            return
    except IndexError:
        folder = hf.get_branch_location()
        commits = hf.get_immediate_subdirectories(folder)
        print "List of all commits. Type '$jet list <commit_number>' " \
              "to see more information"
        commits.reverse()
        for commit_num in commits:
            print "Commit number: %s" % commit_num
        return
    folder = hf.get_branch_location()
    commits = hf.get_immediate_subdirectories(folder)
    found = False
    for commit in commits:
        if commit == commit_number:
            found = True
            filename = os.path.join(hf.get_branch_location() +
                                    '/%s/file_log.txt' % commit_number)
            with open(filename, 'r') as file_:
                lines = file_.read().splitlines()
            try:
                line_number = sys.argv[3]
                try:
                    line = lines[int(line_number)]
                    try:
                        filename = os.path.join(hf.get_branch_location()
                                                + '/%s/%s/changes.txt' %
                                                (commit_number, line_number))
                        with open(filename, 'r') as file_:
                            to_print = file_.read().splitlines()
                        print "Changes to file %s" % line
                        for line_to_print in to_print:
                            print "    %s" % line_to_print
                    except IOError:
                        print "That line number was not " \
                              "an edited file, therefore there is no more" \
                              " information on it"
                except (IndexError, TypeError):
                    print "Incorrect line number, type " \
                          "'$jet list %s' to see the possible" \
                          " lines numbers." % commit_number
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
            print "Type '$jet list %s <line_number>'" \
                  " to see more information about that change" % commit_number

    if not found:
        print "Incorrect commit number, type '$jet list' to see all commits"


def run():
    list_commits()