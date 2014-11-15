#Purpose of this file is to test the local version of the version control
from jet_files import helper_functions
RESULTS = []
EXPECTED_RESULT = "No changes found"


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
    test_list = [
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '10',
        '11',
        '12',
        '13',
        '14',
        '15',
        '16',
        '17',
        '18',
        '19',
        '20',
    ]
    for test in test_list:
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
    number_of_tests = 12
    for i in range(1, number_of_tests + 1):
        parent_filename = 'tests/merge/%s/parent.txt' % i
        with open(parent_filename, 'r') as myFile:
            parent = myFile.read().splitlines()
        file1_filename = 'tests/merge/%s/file1.txt' % i
        with open(file1_filename, 'r') as myFile:
            file1 = myFile.read().splitlines()
        file2_filename = 'tests/merge/%s/file2.txt' % i
        with open(file2_filename, 'r') as myFile:
            file2 = myFile.read().splitlines()
        result_filename = 'tests/merge/%s/expected_result.txt' % i
        with open(result_filename, 'r') as myFile:
            expected_result = myFile.read().splitlines()
        result = helper_functions.fix_file("irrelevant",
                                           parent, file1, file2, test=True)
        if i == 12:
            import ipdb; ipdb.set_trace()
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


def run():
    print "Beginning tests..."
    test_diff_algorithm()
    test_merging()
    number_of_tests = len(RESULTS)
    passed = 0
    for result in RESULTS:
        if result == 'Passed':
            passed += 1
        print result
    print "Passed %s out of %s tests" % (passed, number_of_tests)