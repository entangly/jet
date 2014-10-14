from shutil import copyfile
from jet_files import helper_functions as hf
import os
from os import walk


def init():
    if hf.already_initialized():
        print "Already a repo initialized"
    else:
        os.mkdir('.jet')
        f = []
        filenames_list = []
        for (dirpath, dirnames, filenames) in walk(os.getcwd()):
            for filename in filenames:
                if not filename.endswith("~"):
                    filenames_list.append(filename)
                    f.append(os.path.join(dirpath, filename))
        with open('.jet/latest_saved_files', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "~J/ET")
                file_.write(hf.checksum_md5(file_to_add) + "~J/ET")
        os.mkdir('.jet/0/')
        with open('.jet/0/file_log.txt', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "\n")

        count = 0
        for file_to_add in f:
            folder = os.path.join(hf.get_jet_directory() +
                                  '/.jet/%s/%s' % (0, count))
            os.mkdir(folder)
            filename = os.path.join(hf.get_jet_directory() +
                                    '/.jet/%s/%s/filename.txt'
                                    % (0, count))
            with open(filename, 'w') as myFile:
                    myFile.write(file_to_add)
            filename = filenames_list[count]
            copyfile(file_to_add, '.jet/0/%s/%s' % (count, filename))
            count += 1
        filename = '.jet/branch'
        with open(filename, 'w') as file_:
            file_.write("master")
        print "Initializing Jet repository in %s" % os.getcwd()


def run():
    init()