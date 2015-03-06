import os
import sys
from jet_files import helper_functions as hf
import requests
import json

#DOMAIN = 'http://0.0.0.0:8000/'
DOMAIN = 'http://www.jetvc.co.uk/'


def push():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    jet_directory = hf.get_jet_directory()
    branch = hf.get_branch()
    if not hf.is_setup():
        print "You must setup before pushing! To do this type:" \
              " $jet setup"
        return
    hook = hf.get_push_hook()
    if hook:
        result = hf.run_hook(hook)
        if result:
            print "Hook passed."
        else:
            print "Hook Failed. Not pushing"
            return
    branch, last_update = hf.get_last_update(branch)
    current_commit = hf.get_commit()
    if int(last_update) == int(current_commit):
        print "No changes to push"
        return

    print "Connecting...."
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          branch)
    try:
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception, e:
        print "Failed to connect to Jets servers."
        print "Error - %s" % e
        return
    # Change to only commited files
    current_files = hf.get_file_list_at(branch, hf.get_commit())
    # Send commit POST
    print "Creating commit on server..."
    url = "%screate_commit/" % DOMAIN
    if sys.argv[2] == "-m" and len(sys.argv) == 4:
        message = sys.argv[3]
    else:
        message = "Pushed from local servers"
    data = {
        'message': message,
        'user_id': hf.get_user_id(),
        'branch_name': branch,
        'repo_id': hf.get_repo_id(),
    }
    response = requests.post(url, data=data)
    commit_id = response.headers['commit_id']
    for _file in content['files']:
        filename = jet_directory + '/' + _file['filename']
        try:
            current_files.remove(filename)
        except ValueError:
            continue
        try:
            current_hash = hf.checksum_md5(filename)
        except IOError:
            current_hash = "Not a file"
        if current_hash == _file['hash']:
            # File is unchanged
            continue
        with open(filename, 'r') as myFile:
            contents = myFile.read()
        print "Uploading file %s..." % filename
        stripped_filename = filename[len(jet_directory):]
        if stripped_filename.startswith('/'):
            stripped_filename = stripped_filename[1:]
        url = "%supdate_file/" % DOMAIN
        data = {
            'filename': stripped_filename,
            'api_key': hf.get_user_id(),
            'branch_name': branch,
            'repo_id': hf.get_repo_id(),
            'contents': contents,
            'commit_id': commit_id,
        }
        requests.post(url, data=data)

    for new_file in current_files:
        filename = new_file
        with open(filename, 'r') as myFile:
            contents = myFile.read()
        print "Uploading file %s..." % hf.relative(filename, os.getcwd())
        stripped_filename = filename[len(jet_directory):]
        if stripped_filename.startswith('/'):
            stripped_filename = stripped_filename[1:]
        url = "%supdate_file/" % DOMAIN
        data = {
            'filename': stripped_filename,
            'branch_name': branch,
            'api_key': hf.get_user_id(),
            'repo_id': hf.get_repo_id(),
            'contents': contents,
            'commit_id': commit_id,
        }
        requests.post(url, data=data)

    hf.add_update(branch, hf.get_commit())
    last_server_pull = hf.get_last_server_pull(branch)
    hf.save_last_pull(branch, last_server_pull + 1)
    print hf.BColors.GREEN + "Pushed" + hf.BColors.ENDC


def run():
    push()