# -*- coding: utf-8 -*-

import ldtp
import ldtputils

from time import time, gmtime, strftime

from desktoptesting.gnome import GEdit
from desktoptesting.check import FileComparison

try:

    test = GEdit()

    dataXml  = ldtputils.LdtpDataFileParser(datafilename)    
    oracle = dataXml.gettagvalue("oracle")[0]
    chain  = dataXml.gettagvalue("string")[0]
    test_file = strftime("/tmp/" + "%Y%m%d_%H%M%S" + ".txt", gmtime((time())))
    
    start_time = time()
    
    test.open()
    test.write_text(chain)
    test.save(test_file)
    test.exit()

    stop_time = time()
    
    elapsed = stop_time - start_time
    
    testcheck = FileComparison(oracle, test_file)
    check = testcheck.perform_test()

    ldtp.log (str(elapsed), 'time')
    
    if check == desktoptesting.check.FAIL:
        ldtp.log ('Files differ.', 'cause')
        ldtp.log ('Files differ.', 'error')

except ldtp.LdtpExecutionError, msg:
    raise



