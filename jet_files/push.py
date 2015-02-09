from jet_files import helper_functions as hf
import requests
import json

BRANCH = hf.get_branch()
JET_DIRECTORY = hf.get_jet_directory()
DOMAIN = 'http://0.0.0.0:8000/'


def push():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return
    if not hf.logged_in():
        print "You must login before pushing! To do this type:" \
              " $jet login <username>"
        return
    hook = hf.get_push_hook()
    if hook:
        result = hf.run_hook(hook)
        if result:
            print "Hook passed."
        else:
            print "Hook Failed. Not pushing"
            return

    print "Connecting...."
    url = "%scurrent_file_list/%s/%s/" % (DOMAIN,
                                          hf.get_repo_id(),
                                          BRANCH)
    try:
        response = requests.get(url)
        content = json.loads(response.content)
    except Exception, e:
        print "Failed to connect to Jets servers."
        print "Error - %s" % e
        return
    # Change to only commited files
    current_files = hf.get_file_list_at(BRANCH, hf.get_commit())
    # Send commit POST
    print "Creating commit on server..."
    url = "%screate_commit/" % DOMAIN
    data = {
        'message': "Pushed from local servers",
        'user_id': hf.get_user_id(),
        'branch_name': BRANCH,
        'repo_id': hf.get_repo_id(),
    }
    response = requests.post(url, data=data)
    commit_id = response.headers['commit_id']
    for _file in content['files']:
        filename = JET_DIRECTORY + '/' + _file['filename']
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
        stripped_filename = filename[len(JET_DIRECTORY):]
        if stripped_filename.startswith('/'):
            stripped_filename = stripped_filename[1:]
        url = "%supdate_file/" % DOMAIN
        data = {
            'filename': stripped_filename,
            'branch_name': BRANCH,
            'repo_id': hf.get_repo_id(),
            'contents': contents,
            'commit_id': commit_id,
        }
        requests.post(url, data=data)

    for new_file in current_files:
        filename = new_file
        with open(filename, 'r') as myFile:
            contents = myFile.read()
        print "Uploading file %s..." % filename
        stripped_filename = filename[len(JET_DIRECTORY):]
        if stripped_filename.startswith('/'):
            stripped_filename = stripped_filename[1:]
        url = "%supdate_file/" % DOMAIN
        data = {
            'filename': stripped_filename,
            'branch_name': BRANCH,
            'repo_id': hf.get_repo_id(),
            'contents': contents,
            'commit_id': commit_id,
        }
        requests.post(url, data=data)

    print hf.BColors.GREEN + "Pushed" + hf.BColors.ENDC


def run():
    push()