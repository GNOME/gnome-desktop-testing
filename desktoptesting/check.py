"""
This is the check.py module.

The check module provides different ways to check if the test failed or passed
"""
import filecmp
import os
import sys

FAIL = "fail"
PASS = "pass"

class Check:
    """
    Superclass for the rest of the test checks
    """
    def __init__(self):
        return

class FileComparison(Check):
    """
    Test check for file comparison. If two files are equal, the test passes.
    """
    def __init__(self, oracle, test):
        """
        Main constructor. It requires two existing files paths.

        @type oracle: string
        @param oracle: The path to the oracle file to compare the test file against.

        @type test: string
        @param test: The path to the test file to compare the test file against.
        """

        Check.__init__(self)

        if not (os.path.exists(oracle) and os.path.exists(test)):
            print "Both oracle and test file must exist"
            sys.exit(0)

        self.oracle = oracle
        self.test   = test

    def perform_test(self):
        """
        Perform the test check. 

        It the two files are equal, the test passes. Otherwise, it fails.
        """
        if filecmp.cmp(self.oracle, self.test):
            return PASS
        else:
            return FAIL



