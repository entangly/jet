from jet_files import helper_functions as hf


def status():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if len(hf.get_current_files()) == len(hf.get_stored_files()) and len(
            hf.get_changed_files()) == 0:
        print "Nothing has changed!"
        deleted_files = []
    else:
        print "Your repo has changed since the last commit"
        new_files = hf.get_new_files()
        if new_files:
            new_files_in_changeset = hf.get_new_files_in_changeset()
            if new_files_in_changeset:
                unadded_new = []
                for new_file in new_files:
                    if new_file not in new_files_in_changeset:
                        unadded_new.append(new_file)
                print "New files in changeset:"
                for new_file_in_changeset in new_files_in_changeset:
                    print "    %s" % new_file_in_changeset
            else:
                unadded_new = new_files
            if unadded_new:
                print "New files:"
                for new_file in unadded_new:
                    print "    %s" % new_file
        deleted_files = hf.get_deleted_files()
    if deleted_files:
        deleted_files_in_changeset = hf.get_deleted_files_in_changeset()
        if deleted_files_in_changeset:
            unadded_deleted = []
            for deleted_file in deleted_files:
                if deleted_file not in deleted_files_in_changeset:
                    unadded_deleted.append(deleted_file)
            print "Deleted files in changeset:"
            for deleted_file_in_changeset in deleted_files_in_changeset:
                print "    %s" % deleted_file_in_changeset
        else:
            unadded_deleted = deleted_files
        if unadded_deleted:
            print "Deleted files:"
            for deleted_file in unadded_deleted:
                print "    %s" % deleted_file

    changed_files = hf.get_changed_files()
    if changed_files:
        changed_files_in_changeset = hf.get_changed_files_in_changeset()
        if changed_files_in_changeset:
            unadded = []
            for file_ in changed_files:
                if file_ not in changed_files_in_changeset:
                    unadded.append(file_)
            print "Changed files in changeset:"
            for changed_file_in_changeset in changed_files_in_changeset:
                print "    %s" % changed_file_in_changeset
        else:
            unadded = changed_files
        if unadded:
            print "Changed files:"
            for changed_file in unadded:
                print "    %s" % changed_file


def run():
    status()