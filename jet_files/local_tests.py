#Purpose of this file is to test the local version of the version control
from jet_files import helper_functions
RESULTS = []


def test_same_files():
    diff = helper_functions.diff('.jet/temp', "one.py")
    expected_result = "No changes found"
    if diff == expected_result:
        RESULTS.append("Passed")
    else:
        #RESULTS.append("Failed")
        #RESULTS.append("Expected %s" % expected_result)
        RESULTS.append(diff)


def test_diff_algorithm():
    print "Testing diff algorithm"
    test_same_files()


def run():
    print "Beginning tests..."
    test_diff_algorithm()
    for result in RESULTS:
        print result