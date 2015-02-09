import json
import os
from jet_files import helper_functions as hf
import requests


BRANCH = hf.get_branch()
JET_DIRECTORY = hf.get_jet_directory()
DOMAIN = 'http://0.0.0.0:8000/'


def pull():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    print "Connecting...."
    url = "%shighest_commit/%s/%s/" % (DOMAIN,
                                       hf.get_repo_id(),
                                       BRANCH)
    try:
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception, e:
        print "Failed to connect to Jets servers."
        print "Error - %s" % e
        return
    server_commit = content['commit_number']
    print "Connected."
    last_server_pull = hf.get_last_server_pull(BRANCH)
    if server_commit == last_server_pull:
        print "You are already upto date."
        return

    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          BRANCH)
    response = requests.get(url)
    content = json.loads(response.content)
    current_files = hf.get_current_files()
    for _file in content['files']:
        filename = JET_DIRECTORY + '/' + _file['filename']
        current_files.remove(filename)
        try:
            current_hash = hf.checksum_md5(filename)
        except IOError:
            current_hash = "Not a file"
        if current_hash == _file['hash']:
            # File is unchanged
            continue
        # File is either new or edited
        print "Updating file %s..." % filename
        url = "%sapi/v1/file/%s" % (DOMAIN, _file['file_id'])
        response = requests.get(url)
        content = json.loads(response.content)
        new_contents = content['contents']
        with open(filename, 'w') as new_file:
            new_file.write(new_contents)

    for file_to_delete in current_files:
        os.remove(file_to_delete)

    hf.save_last_pull(BRANCH, server_commit)
    print hf.BColors.GREEN + "Pulled" + hf.BColors.ENDC


def run():
    pull()