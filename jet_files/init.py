from jet_files import helper_functions as hf
import os
from os import walk


def init():
    if hf.already_initialized():
        print "Already a repo initialized"
    else:
        os.mkdir('.jet')
        f = []
        for (dirpath, dirnames, filenames) in walk(os.getcwd()):
            for filename in filenames:
                if not filename.endswith("~"):
                    f.append(os.path.join(dirpath, filename))
        with open('.jet/latest_saved_files', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "~J/ET")
                file_.write(hf.checksum_md5(file_to_add) + "~J/ET")
        os.mkdir('.jet/0/')
        with open('.jet/0/file_list.txt', 'w') as file_:
            for file_to_add in f:
                file_.write(file_to_add + "\n")

        print "Initializing Jet repository in %s" % os.getcwd()


def run():
    init()