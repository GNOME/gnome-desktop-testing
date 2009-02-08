# -*- coding: utf-8 -*-

from ooldtp import *
from ldtp import *
from ldtputils import *

from time import *

from gnometesting.gnome import *
from gnometesting.check import *

try:

    test = GEdit()

    dataXml  = LdtpDataFileParser(datafilename)    
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

    log ('elapsed_time: ' + str(elapsed), 'comment')
    
    if check == FAIL:
        log ('Files differ.', 'CAUSE')
        log ('Files differ.', 'ERROR')

except LdtpExecutionError, msg:
    raise



