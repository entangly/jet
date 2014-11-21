#Purpose of this file is to test the local version of the version control
import os
import shutil
from jet_files import helper_functions, init

RESULTS = []
EXPECTED_RESULT = "No changes found"
cwd = os.getcwd()
directory = os.path.join(cwd + '/tests/test_directory/')
file1 = os.path.join(directory + 'one.py')
file2 = os.path.join(directory + 'one/two.py')
file3 = os.path.join(directory + 'one/one.py')
file4 = os.path.join(directory + 'three.py')
file5 = os.path.join(directory + 'four.py')
file6 = os.path.join(directory + 'five/five.py')
file7 = os.path.join(directory + 'five/six/seven/eight/six.py')


def test_same_files():
    test_list = ['1',
                 '2',
                 '3',
                 '4',
                 '5']
    for test in test_list:
        #RESULTS.append("Testing where the file is the same, number %s" % test)
        diff = helper_functions.diff('tests/diff/same/%s/before.txt' % test,
                                     "tests/diff/same/%s/after.txt" % test)

        if diff == EXPECTED_RESULT:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Same Test '%s' Failed" % test)
            RESULTS.append("Expected %s" % EXPECTED_RESULT)
            RESULTS.append("Received:\n %s" % diff)


def test_different_files():
    number_of_tests = 20
    for test in range(0, number_of_tests + 1):
        diff = helper_functions.diff('tests/diff/different/%s/before.txt'
                                     % test,
                                     "tests/diff/different/%s/after.txt"
                                     % test)

        answer = helper_functions.reform_file('tests/diff/different/'
                                              '%s/before.txt' % test,
                                              diff.splitlines())

        difference = helper_functions.diff('tests/diff/different/%s/after.txt'
                                           % test,
                                           answer)

        if difference == EXPECTED_RESULT:
            RESULTS.append("Passed")
        else:
            RESULTS.append("Different Test '%s' Failed" % test)


def test_diff_algorithm():
    print "Testing diff algorithm"
    try:
        test_same_files()
    except Exception, e:
        print e
        RESULTS.append('FAILED DIFF')
    try:
        test_different_files()
    except Exception, e:
        print e
        RESULTS.append('FAILED DIFF')


def test_merges():
    number_of_tests = 15
    for i in range(1, number_of_tests + 1):
        parent_filename = 'tests/merge/%s/parent.txt' % i
        with open(parent_filename, 'r') as myFile:
            parent = myFile.read().splitlines()
        file1_filename = 'tests/merge/%s/file1.txt' % i
        with open(file1_filename, 'r') as myFile:
            fileone = myFile.read().splitlines()
        file2_filename = 'tests/merge/%s/file2.txt' % i
        with open(file2_filename, 'r') as myFile:
            filetwo = myFile.read().splitlines()
        result_filename = 'tests/merge/%s/expected_result.txt' % i
        with open(result_filename, 'r') as myFile:
            expected_result = myFile.read().splitlines()
        result = helper_functions.fix_file("irrelevant",
                                           parent, fileone, filetwo, test=True)
        split_result = result[0].splitlines()
        if helper_functions.diff(split_result, expected_result) \
                == EXPECTED_RESULT \
                or helper_functions.diff(result, expected_result)\
                == EXPECTED_RESULT:
            RESULTS.append('Passed')
        else:
            RESULTS.append("Merging Test '%s' Failed" % i)


def test_merging():
    print "Testing merging algorithm"
    try:
        test_merges()
    except Exception, e:
        RESULTS.append('FAILED MERGING')
        print e


def test_get_jet_directory():
    expected_jet_directory = os.path.join(cwd + '/tests/test_directory')
    jet_directory = helper_functions.get_jet_directory()
    if jet_directory == expected_jet_directory:
        RESULTS.append("Passed")
    else:
        RESULTS.append("Failed get jet directory. Received %s, should be %s"
                       % (jet_directory, expected_jet_directory))


def setup():
    os.mkdir(directory)

    with open(file1, 'w') as myFile:
        myFile.write(file1)

    os.mkdir(os.path.join(directory + 'one/'))
    with open(file2, 'w') as myFile:
        myFile.write(file2)

    with open(file3, 'w') as myFile:
        myFile.write(file3)

    with open(file4, 'w') as myFile:
        myFile.write(file4)

    with open(file5, 'w') as myFile:
        myFile.write(file5)

    os.mkdir(os.path.join(directory + 'five/'))
    os.mkdir(os.path.join(directory + 'five/six/'))
    os.mkdir(os.path.join(directory + 'five/six/seven/'))
    os.mkdir(os.path.join(directory + 'five/six/seven/eight/'))

    with open(file6, 'w') as myFile:
        myFile.write(file6)

    with open(file7, 'w') as myFile:
        myFile.write(file7)

    os.chdir(directory)
    init.init()


def clear_up():
    shutil.rmtree(directory)
    os.chdir(cwd)


def test_current_files():
    expected_files = [file1, file2, file3, file4, file5, file6, file7]
    current_files = helper_functions.get_current_files()
    for f in expected_files:
        if f not in current_files:
            RESULTS.append("Failed current files")
        else:
            RESULTS.append("Passed")
    if not len(expected_files) == len(current_files):
        RESULTS.append("Failed current files length check")
    else:
        RESULTS.append("Passed")


def test_get_new_commit_number(expected_result):
    new_commit = helper_functions.get_new_commit_number()
    if not expected_result == new_commit:
        RESULTS.append("Failed get new commit")
    else:
        RESULTS.append("Passed")


def test_stored_files():
    expected_files = [file1, file2, file3, file4, file5, file6, file7]
    stored_files = helper_functions.get_stored_files()
    for f in expected_files:
        if f not in stored_files:
            RESULTS.append("Failed stored files")
        else:
            RESULTS.append("Passed")
    if not len(expected_files) == len(stored_files):
        RESULTS.append("Failed stored files length check")
    else:
        RESULTS.append("Passed")


def test_get_stored_hash():
    files = [file1, file2, file3, file4, file5, file6, file7]
    for f in files:
        file1hash = helper_functions.checksum_md5(f)
        stored_hash = helper_functions.get_stored_hash(f)
        if not file1hash == stored_hash:
            RESULTS.append("Failed stored hash")
        else:
            RESULTS.append("Passed")


def test_get_new_files_in_changeset(expected_result):
    new_files = helper_functions.get_new_files_in_changeset()
    if not len(new_files) == expected_result:
        RESULTS.append("Failed new files in changeset")
    else:
        RESULTS.append("Passed")


def test_get_deleted_files_in_changeset(expected_result):
    deleted_files = helper_functions.get_deleted_files_in_changeset()
    if not len(deleted_files) == expected_result:
        RESULTS.append("Failed deleted files in changeset")
    else:
        RESULTS.append("Passed")


def test_get_changed_files_in_changeset(expected_result):
    changed_files = helper_functions.get_changed_files_in_changeset()
    if not len(changed_files) == expected_result:
        RESULTS.append("Failed changed files in changeset")
    else:
        RESULTS.append("Passed")


def test_common_functions():
    print "Testing common functions"
    setup()
    try:
        test_get_jet_directory()
        test_current_files()
        test_stored_files()
        test_get_new_commit_number(1)
        test_get_stored_hash()
        test_get_new_files_in_changeset(0)
        test_get_deleted_files_in_changeset(0)
        test_get_changed_files_in_changeset(0)
    except Exception, e:
        RESULTS.append('FAILED')
        print e
    clear_up()


def run():
    print "Beginning tests..."

    test_diff_algorithm()
    test_merging()
    test_common_functions()

    print "Results:"
    number_of_tests = len(RESULTS)
    passed = 0
    for result in RESULTS:
        if result == 'Passed':
            passed += 1
        print "    %s" % result
    print "Passed %s out of %s tests" % (passed, number_of_tests)