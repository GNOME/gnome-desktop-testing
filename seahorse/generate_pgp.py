from ooldtp import *
from ldtp import *
from ldtputils import *
from time import *

from gnometesting.gnome import *

try:
  
    dataXml  = LdtpDataFileParser(datafilename)    
    name     = dataXml.gettagvalue("name")[0]
    email    = dataXml.gettagvalue("email")[0]
    comment  = dataXml.gettagvalue("comment")[0]
    passphrase  = dataXml.gettagvalue("passphrase")[0]

    
    seahorse = Seahorse()
    
    start_time = time()
    
    # Open the update manager and check the repositories
    seahorse.open()
    seahorse.new_pgp_key(name, email, comment, passphrase)
    seahorse.exit()
        
    stop_time = time()
 
    elapsed = stop_time - start_time
    
    log ('elapsed_time: ' + str(elapsed), 'comment')
    
except LdtpExecutionError, msg:
    raise



