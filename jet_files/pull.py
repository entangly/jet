import json
import os
from jet_files import helper_functions as hf
import requests


#DOMAIN = 'http://0.0.0.0:8000/'
DOMAIN = 'http://www.jetvc.co.uk/'


def pull():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    branch = hf.get_branch()
    jet_directory = hf.get_jet_directory()
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

    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          branch)
    response = requests.get(url)
    content = json.loads(response.content)
    current_files = hf.get_current_files()
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
        print "Updating file %s..." % filename
        url = "%sapi/v1/file/%s" % (DOMAIN, _file['file_id'])
        response = requests.get(url)
        content = json.loads(response.content)
        new_contents = content['contents']
        if new:
            hf.make_directories(filename)
        with open(filename, 'w') as new_file:
            new_file.write(new_contents)

    for file_to_delete in current_files:
        os.remove(file_to_delete)

    hf.save_last_pull(branch, server_commit)
    print hf.BColors.GREEN + "Pulled" + hf.BColors.ENDC


def run():
    pull()