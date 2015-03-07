import os
from jet_files import helper_functions as hf


def status():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    cwd = os.getcwd()
    branch = hf.get_branch()
    branch_location = hf.get_branch_location_param(branch)
    jet_directory = hf.get_jet_directory()
    print "You are working on branch %s" % branch
    current_files = hf.get_current_files(jet_directory)
    stored_files_and_hashes = hf.get_stored_files_and_hashes()
    stored_files = hf.get_stored_files(stored_files_and_hashes)
    changed_files = hf.get_changed_files(current_files,
                                         stored_files_and_hashes)
    if len(current_files) == len(stored_files)\
            and len(changed_files) == 0:
        print "Nothing has changed!"
    else:
        print "Your repo has changed since the last commit"
        files_in_changeset = hf.get_files_in_changeset(branch_location)
        new_files = hf.get_new_files(current_files, stored_files)
        if new_files:
            new_files_in_changeset =\
                hf.get_new_files_in_changeset(files_in_changeset)
            if new_files_in_changeset:
                unadded_new = []
                for new_file in new_files:
                    if new_file not in new_files_in_changeset:
                        unadded_new.append(new_file)
                print "New files in changeset:"
                for new_file_in_changeset in new_files_in_changeset:
                    print hf.BColors.GREEN + \
                        "    %s" % hf.relative(new_file_in_changeset, cwd) +\
                        hf.BColors.ENDC
            else:
                unadded_new = new_files
            if unadded_new:
                print "New files:"
                for new_file in unadded_new:
                    print hf.BColors.GREEN + \
                        "    %s" % hf.relative(new_file, cwd) + \
                        hf.BColors.ENDC
        deleted_files = hf.get_deleted_files(current_files, stored_files)
        if deleted_files:
            deleted_files_in_changeset =\
                hf.get_deleted_files_in_changeset(files_in_changeset)
            if deleted_files_in_changeset:
                unadded_deleted = []
                for deleted_file in deleted_files:
                    if deleted_file not in deleted_files_in_changeset:
                        unadded_deleted.append(deleted_file)
                print "Deleted files in changeset:"
                for deleted_file_in_changeset in deleted_files_in_changeset:
                    print hf.BColors.RED + \
                        "    %s" % hf.relative(deleted_file_in_changeset, cwd)\
                        + hf.BColors.ENDC
            else:
                unadded_deleted = deleted_files
            if unadded_deleted:
                print "Deleted files:"
                for deleted_file in unadded_deleted:
                    print hf.BColors.RED + \
                        "    %s" % hf.relative(deleted_file, cwd) +\
                        hf.BColors.ENDC

        if changed_files:
            changed_files_in_changeset =\
                hf.get_changed_files_in_changeset(files_in_changeset)
            if changed_files_in_changeset:
                unadded = []
                for file_ in changed_files:
                    if file_ not in changed_files_in_changeset:
                        unadded.append(file_)
                print "Changed files in changeset:"
                for changed_file_in_changeset in changed_files_in_changeset:
                    print hf.BColors.YELLOW + \
                        "    %s" % hf.relative(changed_file_in_changeset, cwd)\
                        + hf.BColors.ENDC
            else:
                unadded = changed_files
            if unadded:
                print "Changed files:"
                for changed_file in unadded:
                    print hf.BColors.YELLOW +\
                        "    %s" % hf.relative(changed_file, cwd) +\
                        hf.BColors.ENDC


def run():
    status()
