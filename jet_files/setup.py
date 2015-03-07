import os
from jet_files import helper_functions as hf
import getpass
import requests

#DOMAIN = 'http://0.0.0.0:8000/'
DOMAIN = 'http://www.jetvc.co.uk/'


def setup():
    if not hf.already_initialized():
        print "Please init a jet repo before calling other commands"
        return

    status_code = 403
    first_time = True
    print "Connecting...."
    # Stop syntax highlighting, set variables
    username = None
    response = None
    while not status_code == 200:
        if not first_time:
            print hf.BColors.RED + \
                "Incorrect details - please try again!" + \
                hf.BColors.ENDC
        print "Please type your Jet username used in registration" \
              " at www.jetvc.co.uk. If you're not already " \
              "registered please visit www.jetvc.co.uk/register/"
        username = raw_input("Username: ")
        password = getpass.getpass()

        url = "%slogin_user/" % DOMAIN
        try:
            data = {
                'username': username,
                'password': password,
            }
            response = requests.post(url, data=data)
            first_time = False
            status_code = response.status_code
        except Exception, e:
            print "Failed to connect to Jets servers."
            print "Error - %s" % e
            return
    print "Congrats you are logged in. These details will be saved"
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/username')
    with open(filename, 'w') as file_:
        file_.write(username + '\n')
        file_.write(response.headers['user_id'])
    print "Re-run setup to change user"

    user_id = response.headers['user_id']

    status_code = 400
    first_time = True
    while not status_code == 200:
        if not first_time:
            print hf.BColors.RED + \
                "Repository name not found - please try again!" + \
                hf.BColors.ENDC
        print "Please type the name of the online repo you wish" \
              " to link this with."
        repo_name = raw_input("Name (case-sensitive): ")
        try:
            url = "%sverify_repo/" % DOMAIN
            data = {
                'repo_name': repo_name,
                'user_id': user_id,
            }
            response = requests.post(url, data=data)
            first_time = False
            status_code = response.status_code
        except Exception, e:
            print "Failed to connect to Jets servers."
            print "Error - %s" % e
            return
    print "All setup."
    print "These details will be saved"
    filename = os.path.join(hf.get_jet_directory()
                            + '/.jet/repo_id')
    with open(filename, 'w') as file_:
        file_.write(response.headers['repo_id'])


def run():
    setup()