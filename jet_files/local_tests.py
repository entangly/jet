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
    try:
        test_different_files()
    except Exception, e:
        print e


def run():
    print "Beginning tests..."
    test_diff_algorithm()
    number_of_tests = len(RESULTS)
    passed = 0
    for result in RESULTS:
        if result == 'Passed':
            passed += 1
        print result
    print "Passed %s out of %s tests" % (passed, number_of_tests)