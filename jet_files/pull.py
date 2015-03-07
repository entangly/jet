import json
import os
import sys
from jet_files import helper_functions as hf
from jet_files import init, commit_changeset, add
import requests


#DOMAIN = 'http://0.0.0.0:8000/'
DOMAIN = 'http://www.jetvc.co.uk/'


def force_pull():
    branch = hf.get_branch()
    jet_directory = hf.get_jet_directory()
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          branch)
    response = requests.get(url)
    content = json.loads(response.content)
    current_files = hf.get_current_files(None)
    for _file in content['files']:
        filename = jet_directory + '/' + _file['filename']
        try:
            current_files.remove(filename)
            new = False
        except ValueError:
            new = True
        try:
            current_hash = hf.checksum_md5(filename)
        except IOError:
            current_hash = "Not a file"
        if current_hash == _file['hash']:
            # File is unchanged
            continue
        # File is either new or edited
        print "Updating file %s..." % hf.relative(filename, os.getcwd())
        url = "%sapi/v1/file/%s/?api_key=%s" % (DOMAIN,
                                                _file['file_id'],
                                                hf.get_user_id())
        response = requests.get(url)
        content = json.loads(response.content)
        new_contents = content['contents']
        if new:
            hf.make_directories(filename, clone=False)
        with open(filename, 'w') as new_file:
            new_file.write(new_contents)

    for file_to_delete in current_files:
        os.remove(file_to_delete)


def clone():
    if hf.already_initialized():
        print "Already a repo here, can't clone into this directory."
        return
    branch = sys.argv[3]
    repo_id = sys.argv[2]
    directory = os.getcwd()
    if not os.listdir(directory) == []:
        print "Can only clone into an empty directory, sorry."
        return
    print "Connecting...."
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          repo_id,
                                          branch)
    try:
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception, e:
        print "Failed to connect to Jets servers."
        print "Error - %s" % e
        return
    if not response.status_code == 200:
        print "There was an error with the repo id or branch name " \
              "- please try again!!!"
        return
    for _file in content['files']:
        filename = directory + '/' + _file['filename']
        print "Adding file %s..." % hf.relative(filename, directory)
        url = "%sapi/v1/file/%s/?api_key=%s" % (DOMAIN,
                                                _file['file_id'],
                                                hf.get_user_id())
        response = requests.get(url)
        content = json.loads(response.content)
        new_contents = content['contents']
        hf.make_directories(filename, clone=True)
        with open(filename, 'w') as new_file:
            new_file.write(new_contents)
    init.run()
    print hf.BColors.GREEN + "Successfully cloned the repo." + hf.BColors.ENDC


def pull():
    branch = hf.get_branch()
    jet_directory = hf.get_jet_directory()
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          branch)
    response = requests.get(url)
    content = json.loads(response.content)
    current_files = hf.get_current_files(None)
    server_files = [jet_directory + '/' + _file['filename']
                    for _file in content['files']]
    server_ids = [_file['file_id'] for _file in content['files']]
    parent_branch, parent_commit_number = hf.get_last_update(branch)
    parent_files = hf.get_file_list_at(parent_branch, parent_commit_number)

    files_to_merge = []
    files_to_ask_about = []

    for file_ in current_files:
        if file_ in server_files:
            files_to_merge.append(file_)
        else:
            files_to_ask_about.append(file_)
    files_to_ask_about += [x for x in server_files if x not in current_files]

    for f in files_to_ask_about:
        answer = hf.ask(f)
        if not answer:
            os.remove(f)
        else:
            if f not in current_files:
                print "Downloading file %s..." % hf.relative(f, os.getcwd())
                url = "%sapi/v1/file/%s/?api_key=%s" \
                      % (DOMAIN,
                         server_ids[server_files.index(f)],
                         hf.get_user_id())
                response = requests.get(url)
                content = json.loads(response.content)
                new_contents = content['contents']
                with open(f, 'w') as myFile:
                    myFile.write(new_contents)
    print "Checking for changes / merges"
    for f in files_to_merge:
        if f in parent_files:
            parent_file = hf.get_file_at(parent_branch,
                                         parent_commit_number,
                                         f)
        else:
            parent_file = []

        with open(f, 'r') as myFile:
            local_file = myFile.read().splitlines()

        url = "%sapi/v1/file/%s/?api_key=%s"\
              % (DOMAIN,
                 server_ids[server_files.index(f)],
                 hf.get_user_id())
        response = requests.get(url)
        content = json.loads(response.content)
        new_contents = content['contents']
        server_file = new_contents.splitlines()

        if not local_file == server_file:
            try:
                new_file = hf.fix_file(f, parent_file, local_file, server_file)
            except IndexError:
                # error has happened. Apply worst case scenario.
                new_file = \
                    ['@@@@@@@@@@HEAD@@@@@@@@@@\n'] \
                    + local_file \
                    + ['\n@@@@@@@@@@SEPARATOR@@@@@@@@@@\n'] \
                    + server_file \
                    + ['\n@@@@@@@@@@END@@@@@@@@@@']
                hf.add_conflict(f)
            with open(f, 'w') as myFile:
                for line in new_file:
                    myFile.write('%s\n' % line)


def run():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    branch = hf.get_branch()
    print "Connecting...."
    url = "%shighest_commit/%s/%s/" % (DOMAIN,
                                       hf.get_repo_id(),
                                       branch)
    try:
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception, e:
        print "Failed to connect to Jets servers."
        print "Error - %s" % e
        return
    server_commit = content['commit_number']
    print "Connected."
    last_server_pull = hf.get_last_server_pull(branch)
    if server_commit == last_server_pull:
        print "You are already upto date."
        return
    try:
        if sys.argv[2] == '-f':
            force_pull()
        else:
            print "Invalid argument."
            return
    except IndexError:
        pull()
    add.add(verbose=False)
    commit_changeset.commit("Merged branch %s with servers changes."
                            % branch, verbose=False)
    hf.save_last_pull(branch, server_commit)
    print "Committed merges"
    print hf.BColors.GREEN + "Pulled" + hf.BColors.ENDC