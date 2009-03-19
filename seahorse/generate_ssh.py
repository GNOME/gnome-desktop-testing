import ldtp 
import ldtputils 
from time import time 

from desktoptesting.gnome import Seahorse

class SeahorseSSH(Seahorse):
    def test_generate_ssh(self, description, set_up, passphrase, computer='', login=''):
        # Create the new key
        self.new_ssh_key(description, set_up, passphrase, computer, login)

        # Check that the key was successfully created
        if self.assert_exists_key(description) == False:
            raise AssertionError, "The key was not succesfully created."

