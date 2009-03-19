import ldtp 
import ldtputils 
from time import time 

from desktoptesting.gnome import Seahorse

    
class SeahorsePGP(Seahorse):
    def test_generate_pgp(self, name, email, comment, passphrase):
        
        # Open the update manager and check the repositories
        self.new_pgp_key(name, email, comment, passphrase)

        if self.assert_exists_key(name) == False:
            raise AssertionError, "The key was not succesfully created."



