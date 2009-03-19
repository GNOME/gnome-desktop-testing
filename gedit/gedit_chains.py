# -*- coding: utf-8 -*-

import ldtp
import ldtputils

from time import time, gmtime, strftime

from desktoptesting.gnome import GEdit
from desktoptesting.check import FileComparison, FAIL

class GEditChain(GEdit):
    def testChain(self, oracle=None, chain=None):
        test_file = strftime(
            "/tmp/" + "%Y%m%d_%H%M%S" + ".txt", gmtime((time())))

        self.write_text(chain)
        self.save(test_file)

        testcheck = FileComparison(oracle, test_file)

        if testcheck.perform_test() == FAIL:
            raise AssertionError, "Files differ"

if __name__ == "__main__":
    gedit_chains_test = GEditChain()
    gedit_chains_test.run()
