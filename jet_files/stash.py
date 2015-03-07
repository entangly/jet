import os
import shutil
import helper_functions as hf


def stash():
    jet_directory = hf.get_jet_directory()
    stash_path = os.path.join(jet_directory + '/.jet/stash/')
    if os.path.exists(stash_path):
        response = raw_input("Are you sure you wish to overwrite your"
                             " previous stash? (y/n) ")
        if not response == "y" or response == "yes":
            print "Cancelling...."
            return
        shutil.rmtree(stash_path)
    os.mkdir(stash_path)
    f = []  # Full filenames
    filenames_list = []  # Names of the files
    # Goes through all files in the current directory and below.
    for (dirpath, dirnames, filenames) in os.walk(jet_directory):
        for filename in filenames:
            # Checks they're not in the jet ignore file
            if hf.filter_one_file_by_ignore(filename):
                if not dirpath\
                        .startswith(os.path.join(jet_directory + '/.jet')):
                    filenames_list.append(filename)
                    f.append(os.path.join(dirpath, filename))
    count = 0
    for file_to_add in f:
        # A folder for each file, to store filename and contents separately.
        folder = os.path.join(stash_path + '/%s' % count)
        os.mkdir(folder)
        # Storing filename..
        filename = os.path.join(stash_path + '/%s/filename.txt' % count)
        with open(filename, 'w') as myFile:
                myFile.write(file_to_add)
        filename = filenames_list[count]
        # Copying the contents over, to enable diffs to work
        new_filename = os.path.join(stash_path + '/%s/%s' % (count, filename))
        shutil.copyfile(file_to_add, new_filename)
        count += 1
    print "Successfully stashed the code"


def unstash():
    jet_directory = hf.get_jet_directory()
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    stash_path = os.path.join(jet_directory + '/.jet/stash/')
    if not os.path.exists(stash_path):
        print "Cannot unstash as there is no stashed content"
        return
    print "Are you sure you wish to restore the code that is stashed?" \
          " Any un-committed changes will be lost."
    response = raw_input("This action is irreversible. (y/n) ")
    if not response == "y" or response == "yes":
        print "Cancelling..."
        return

    current_files = hf.get_current_files(None)
    files = os.listdir(stash_path)
    for _file in files:
        stored_filename_filename = os.path.join(stash_path
                                                + '/%s/filename.txt' % _file)
        with open(stored_filename_filename, 'r') as myFile:
            filename = myFile.read()
        try:
            current_files.remove(filename)
            new = False
        except ValueError:
            new = True
        try:
            current_hash = hf.checksum_md5(filename)
        except IOError:
            current_hash = "Not a file"
        head, name = os.path.split(filename)
        stored_contents_filename = os.path.join(stash_path +
                                                '/%s/%s' % (_file, name))
        with open(stored_contents_filename, 'r') as myFile:
            stored_contents = myFile.read()
        stored_contents_hash = hf.checksum_md5(stored_contents_filename)
        if current_hash == stored_contents_hash:
            # File is unchanged
            continue
        # File is either new or edited
        if new:
            hf.make_directories(filename, clone=False)
        print "Updating %s" % hf.relative(filename, os.getcwd())
        with open(filename, 'w') as new_file:
            new_file.write(stored_contents)

    for file_to_delete in current_files:
        os.remove(file_to_delete)

    print "Loaded in the code from the stash"


def run():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return

    stash()