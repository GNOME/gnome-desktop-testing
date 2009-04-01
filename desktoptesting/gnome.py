"""
This is the "gnome" module.

The gnome module provides wrappers for LDTP to make the write of Gnome tests easier. 
"""
import ooldtp
import ldtp 

class Application:
    """
    Superclass for the rest of the applications

    Constants that should be defined in the classes that inherit from this class
    LAUNCHER: Argument to be passed when launching the application through ldtp.launchapp
    WINDOW: Top application frame pattern using ldtp syntax
    CLOSE_TYPE: Close object type (one of 'menu' or 'button')
    CLOSE_NAME: Close object name
    """
    CLOSE_TYPE = 'menu'
    CLOSE_NAME = 'mnuQuit'
    WINDOW     = ''
    TOP_PANEL = 'frmTopExpandedEdgePanel'


    def __init__(self, name = None, close_type= None, close_name= None):
        """
        @type close_type: string
        @param close_type: The type of close widget of the application. Types: menu, button.
        @type close_name: string
        @param close_name: The name of the exit widget of the application. If not mentioned the default will be used ("Quit")
        """
        if name:
            self.name = name
        else:
            self.name = self.WINDOW

        if close_type:
            self.close_type = close_type
        else:
            self.close_type = self.CLOSE_TYPE

        if close_name:
            self.close_name = close_name
        else:
            self.close_name = self.CLOSE_NAME


    def setup(self):
        pass

    def teardown(self):
        pass

    def cleanup(self):
        self.set_name(self.WINDOW)
        self.set_close_type(self.CLOSE_TYPE)
        self.set_close_name(self.CLOSE_NAME)

    def recover(self):
        self.teardown()
        sleep(1)
        self.setup()

    def set_name(self, name):
        if name is not None:
            self.name = name

    def set_close_type(self, close_type):
        if close_type is not None:
            self.close_type = close_type

    def set_close_name(self, close_name):
        if close_name is not None:
            self.close_name = close_name

    def remap(self):
        """
        It reloads the application map for the given ooldtp.context.
        """
        ldtp.remap(self.name)

    def open_and_check_app(self):
        """
        Given an application, it tries to open it.
         
        """
        ldtp.launchapp(self.LAUNCHER)

        ldtp.wait(2)
        response = ldtp.waittillguiexist(self.name, '', 20)
        
        if response == 0:
            raise ldtp.LdtpExecutionError, "The " + self.name + " window was not found."    

    def exit(self):
        """
        Given an application, it tries to quit it. 
        """
        try:
            app = ooldtp.context(self.name)
            try:
                close_widget = app.getchild(self.close_name)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The " + self.close_name + " widget was not found."

            if self.close_type == 'menu':
                close_widget.selectmenuitem()
            elif self.close_type == 'button':
                close_widget.click()
            else:
                raise ldtp.LdtpExecutionError, "Wrong close item type."
            response = ldtp.waittillguinotexist(self.name, '', 20)
            if response == 0:
                raise ldtp.LdtpExecutionError, "Mmm, something went wrong when closing the application."
        except ldtp.LdtpExecutionError, msg:
            raise ldtp.LdtpExecutionError, "Mmm, something went wrong when closing the application: " + str(msg)

    def save(self, save_menu='mnuSave'):
        """
        Given an application, it tries to save the current document. 
        This method gives very basic functionality. Please, override this method in the subclasses for error checking.
         
        @type save_menu: string
        @param save_menu: The name of the Save menu of the application. If not mentioned the default will be used ("Save").
        """
        try:
            app = ooldtp.context(self.name)
            try:
                actualMenu = app.getchild(save_menu)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The " + save_menu + " menu was not found."

            actualMenu.selectmenuitem()
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "Mmm, something went wrong when saving the current document."

    def write_text(self, text, txt_field=''):
        """
        Given an application it tries to write text to its current buffer.
        """
        app = ooldtp.context(self.name)

        if txt_field == '':
            try:
                ldtp.enterstring(text)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "We couldn't write text."
        else:
            try:
                app_txt_field = app.getchild(txt_field)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The " + txt_field + " text field was not found."
            try:
                app_txt_field.settextvalue(text)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "We couldn't write text."


class Seahorse(Application):
    """
    Seahorse manages the Seahorse application.
    """
    WINDOW       = "frmPasswordsandEncryptionKeys"
    LAUNCHER     = "seahorse"
    MNU_NEWKEY   = "mnuNew"
    NEWKEY_DLG   = "Create New ..."
    BTN_CONTINUE = "btnContinue"
    TYPE_PGP            = "PGP Key"
    NEWPGP_DLG          = "dlgCreateaPGPKey"
    DLG_NEWPGP_FULLNAME = "txtFullName"
    DLG_NEWPGP_EMAIL    = "txtEmailAddress"
    DLG_NEWPGP_COMMENT  = "txtComment"
    BTN_NEWPGP_CREATE   = "btnCreate"
    DLG_NEWKEY_PASS     = "dlgPassphrasefor*"
    BTN_PASS_OK         = "btnOK"
    DLG_GENERATING_KEY  = "dlgGeneratingkey"
    DLG_CREATING_SSH    = "dlgCreatingSecureShellKey"
    TYPE_SSH            = "Secure Shell Key"
    NEWSSH_DLG          = "New Secure Shell Key" 
    DLG_NEWSSH_DESC     = "txtKeyDescription"
    BTN_NEWSSH_CREATE_AND_SETUP = "Create and Set Up"
    DLG_SET_UP          = "Set Up Computer for SSH Connection"
    TXT_SET_UP_COMPUTER = "txtThehostnameoraddressoftheserver."
    TXT_SET_UP_LOGIN    = "txtLoginName"
    BTN_SET_UP          = "btnSetUp"
    BTN_NEWSSH_CREATE   = "Just Create Key"
    TAB_PERSONAL_KEYS   = "My Personal Keys"
    TAB_LIST            = "ptl0"

    def __init__(self):
        Application.__init__(self)

    def setup(self):
        self.open()

    def teardown(self):
        self.exit()

    def cleanup(self):
        #TODO: it should delete all the "My Personal Keys"
        pass

    def open(self):
        self.open_and_check_app()

    def new_key(self, key_type):
        """
        It opens up the list of available new keys, and select the one to create.
        
        @type key_type: string
        @param key_type: The type of key to create. 
        """
        
        seahorse = ooldtp.context(self.name)
        
        try:
            mnu_new_key = seahorse.getchild(self.MNU_NEWKEY)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new key menu was not found."

        try:
            mnu_new_key.selectmenuitem() 
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when selecting new key menu item."

        try:
            ldtp.waittillguiexist(self.NEWKEY_DLG)
            dlg_new_key = ooldtp.context(self.NEWKEY_DLG)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new key dialog was not found."

        try:
            table  = dlg_new_key.getchild(role = 'table')
            types_table = table[0]

            for i in range(0, types_table.getrowcount(), 1):
                text = types_table.getcellvalue(i, 1)
                candidate = text.split('\n')[0]
                if candidate == key_type:
                    types_table.selectrowindex(i)
                    break
                ldtp.wait(1)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "Error getting the key types table."

        try:
            btn_continue = dlg_new_key.getchild(self.BTN_CONTINUE)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The continue button at the new key dialog was not found."

        try:
            btn_continue.click() 
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when clicking the continue button."
        
    def new_pgp_key(self, full_name, email, comment, passphrase):
        """
        It creates a new PGP key with the default settings.

        TODO: Allow advanced options
        TODO: Check the list afterwards for the newly created key

        @type full_name: string 
        @param full_name: Full name to type for the PGP key

        @type email: string 
        @param email: Email to type for the PGP key

        @type comment: string 
        @param comment: Comment to type for the PGP key

        @type passphrase: string 
        @param passphrase: Passphrase to type for the PGP key
        """
        
        self.new_key(self.TYPE_PGP)

        try:
            ldtp.waittillguiexist(self.NEWPGP_DLG)
            dlg_new_pgp = ooldtp.context(self.NEWPGP_DLG)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new key dialog was not found."

        try:
            txt_field = dlg_new_pgp.getchild(self.DLG_NEWPGP_FULLNAME)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The " + txt_field + " text field was not found."
        try:
            txt_field.settextvalue(full_name)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was an error when writing the text."

        try:
            txt_field = dlg_new_pgp.getchild(self.DLG_NEWPGP_EMAIL)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The " + txt_field + " text field was not found."
        try:
            txt_field.settextvalue(email)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when writing the text."
   
        try:
            txt_field = dlg_new_pgp.getchild(self.DLG_NEWPGP_COMMENT)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The " + txt_field + " text field was not found."
        try:
            txt_field.settextvalue(comment)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when writing the text."

        try:
            btn_create = dlg_new_pgp.getchild(self.BTN_NEWPGP_CREATE)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The create button at the new PGP key dialog was not found."

        try:
            btn_create.click() 
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when clicking the create button."
       
        try:
            ldtp.waittillguiexist(self.DLG_NEWKEY_PASS)
            dlg_new_pgp_pass = ooldtp.context(self.DLG_NEWKEY_PASS)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new pgp key passphrase dialog was not found."

        try:
            ldtp.enterstring(passphrase)
            ldtp.enterstring("<tab>")
            ldtp.enterstring(passphrase)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "Error entering passphrase."
 
        try:
            btn_pass_ok = dlg_new_pgp_pass.getchild(self.BTN_PASS_OK)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The OK button at the new PGP key passphrase dialog was not found."

        try:
            btn_pass_ok.click() 
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when clicking the OK button."
 
        try:
            ldtp.waittillguiexist(self.DLG_GENERATING_KEY)
            while ldtp.guiexist(self.DLG_GENERATING_KEY) == 1:
                ldtp.wait(1)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new pgp generating key dialog was not found."


    def new_ssh_key(self, description, passphrase, set_up = False, computer = '', login = ''):
        """
        It creates a new SSH key with the default settings.

        TODO: Setting up the key is not working yet

        @type description: string 
        @param description: Description to type in the SSH key

        @type passphrase: string 
        @param passphrase: Passphrase to type for the SSH key

        @type set_up: boolean 
        @param passphrase: True, to set up the SSH key

        @type computer: string 
        @param computer: URL or IP of the computer to set up the key
        
        @type login: string
        @param login: Login to use in the remote computer
        """
        
        self.new_key(self.TYPE_SSH)

        try:
            ldtp.waittillguiexist(self.NEWSSH_DLG)
            dlg_new_ssh = ooldtp.context(self.NEWSSH_DLG)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new key dialog was not found."

        try:
            txt_field = dlg_new_ssh.getchild(self.DLG_NEWSSH_DESC)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The " + self.DLG_NEWSSH_DESC + " text field was not found."
        try:
            txt_field.settextvalue(description)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was an error when writing the text."

        if set_up == True:
            try:
                btn_create = dlg_new_ssh.getchild(self.BTN_NEWSSH_CREATE_AND_SETUP)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The create button at the new PGP key dialog was not found."

        else:
            try:
                btn_create = dlg_new_ssh.getchild(self.BTN_NEWSSH_CREATE)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The create button at the new PGP key dialog was not found."

        try:
            btn_create.click() 
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when clicking the create button."
      
 
        try:
            ldtp.waittillguiexist(self.DLG_NEWKEY_PASS)
            dlg_new_key_pass = ooldtp.context(self.DLG_NEWKEY_PASS)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new key passphrase dialog was not found."

        try:
            ldtp.enterstring(passphrase)
            ldtp.enterstring("<tab>")
            ldtp.enterstring(passphrase)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "Error entering passphrase."
 
        try:
            btn_pass_ok = dlg_new_key_pass.getchild(self.BTN_PASS_OK)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The OK button at the new key passphrase dialog was not found."

        try:
            btn_pass_ok.click() 
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was a problem when clicking the OK button."
 
        if set_up == True and login is not None:

            try:
                ldtp.waittillguiexist(self.DLG_SET_UP)
                dlg_set_up_computer = ooldtp.context(self.DLG_SET_UP)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The set up computer dialog was not found."

            try:
                txt_field = dlg_set_up_computer.getchild(self.TXT_SET_UP_LOGIN)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The " + self.TXT_SET_UP_LOGIN + " text field was not found."
            try:
                txt_field.settextvalue(login)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "There was an error when writing the text."

        if set_up == True:
            try:
                txt_field = dlg_set_up_computer.getchild(self.TXT_SET_UP_COMPUTER)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The " + self.TXT_SET_UP_COMPUTER + " text field was not found."
            try:
                txt_field.settextvalue(computer)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "There was an error when writing the text."

            try:
                btn_set_up = dlg_set_up_computer.getchild(self.BTN_SET_UP)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The set up button was not found."

            try:
                btn_set_up.click() 
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "There was a problem when clicking the set up button."
            
        try:
            while ldtp.guiexist(self.DLG_CREATING_SSH) == 1:
                ldtp.wait(1)
            
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The creating key dialog was not found."
        
        # It is too fast to grab the main window afterwards
        ldtp.wait(3)

    def assert_exists_key(self, name, tab_name = None):
        """
        It checks that the KEY with description 'description' is
        part of the keys of the current user

        @type name: string
        @param name: The name of the key to search
        
        @type tab_name: string
        @param tab_name: The tab name to search for the key.
        """
        if not tab_name:
            tab_name = self.TAB_PERSONAL_KEYS

        seahorse = ooldtp.context(self.name)
        try:

            page_list = seahorse.getchild(self.TAB_LIST)
            page_list.selecttab(self.TAB_PERSONAL_KEYS)
            scroll_pane = ldtp.getobjectproperty(self.name, tab_name, 'children')
            list_keys = ldtp.getobjectproperty(self.name, scroll_pane, 'children')
            list_keys = list_keys.split(' ')[0]
            list_keys = seahorse.getchild(list_keys)
            for i in range(0, list_keys.getrowcount()):
                current = list_keys.getcellvalue(i, 1)
                if name in current:
                    return True
            
            return False

        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "Error retrieving the list of keys."

class GEdit(Application):
    """
    GEdit manages the Gedit application.
    """
    WINDOW     = "frm*gedit"
    TXT_FIELD  = "txt1"
    LAUNCHER   = "gedit"
    SAVE_DLG   = "dlgSave*"
    SAVE_DLG_TXT_NAME = "txtName"
    SAVE_DLG_BTN_SAVE = "btnSave"
    QUESTION_DLG = "dlgQuestion"
    QUESTION_DLG_BTN_SAVE = "btnSave"
    QUESTION_DLG_BTN_SAVE_AS = "btnSaveAs"
    QUESTION_DLG_BTN_CLOSE = "btnClosewithoutSaving"
    MNU_QUIT = "mnuQuit"
    MNU_CLOSE = "mnuClose"
    MNU_NEW = "mnuNew"

    def __init__(self):
        Application.__init__(self)

    def setup(self):
        self.open()

    def teardown(self):
        self.exit()

    def cleanup(self):
        # Exit using the Quit menu 
        try:
            try:
                gedit = ooldtp.context(self.name)
                quit_menu = gedit.getchild(self.MNU_CLOSE)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The quit menu was not found."
            quit_menu.selectmenuitem()
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "Mmm, something went wrong when closing the application."

        result = ldtp.waittillguiexist(self.QUESTION_DLG,
                                       guiTimeOut = 2)

        if result == 1:
            question_dialog = ooldtp.context(self.QUESTION_DLG)
            question_dlg_btn_close = question_dialog.getchild(self.QUESTION_DLG_BTN_CLOSE)
            question_dlg_btn_close.click()
        
        try:
            gedit = ooldtp.context(self.name)
            new_menu = gedit.getchild(self.MNU_NEW)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The new menu was not found."
        new_menu.selectmenuitem()
        
        result = ldtp.waittillguiexist(
            self.name, self.TXT_FIELD)
        if result != 1:
            raise ldtp.LdtpExecutionError, "Failed to set up new document."
        

    def write_text(self, text):
        """
        It writes text to the current buffer of the Gedit window.

        @type text: string
        @param text: The text string to be written to the current buffer.
        """
        Application.write_text(self, text, self.TXT_FIELD)

    def save(self, filename):
        """
        It tries to save the current opened buffer to the filename passed as parameter.

        TODO: It does not manage the overwrite dialog yet.

        @type filename: string
        @param filename: The name of the file to save the buffer to.
        """
        Application.save(self)
        ooldtp.context(self.name)

        try:
            ldtp.waittillguiexist(self.SAVE_DLG)
            save_dialog = ooldtp.context(self.SAVE_DLG)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The Gedit save dialog was not found."
        try:
            save_dlg_txt_filename = save_dialog.getchild(self.SAVE_DLG_TXT_NAME)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The filename txt field in Gedit save dialog was not found."
        try:
            ldtp.wait(2)
            save_dlg_txt_filename.settextvalue(filename)
        except ldtp.LdtpExecutionError:
           raise ldtp.LdtpExecutionError, "We couldn't write text."

        try:
            save_dlg_btn_save = save_dialog.getchild(self.SAVE_DLG_BTN_SAVE)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The button Save in Gedit save dialog was not found."
        
        try:
            save_dlg_btn_save.click()
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "There was an error when pushing the Save button."

        ldtp.waittillguinotexist(self.SAVE_DLG)
        
    def open(self):
        """
        It opens the gedit application and raises an error if the application
        didn't start properly.

        """
        self.open_and_check_app()

    def exit(self, save=False, filename=''):
        """
        Given a gedit window, it tries to exit the application.
        By default, it exits without saving. This behaviour can be changed to save (or save as) on exit.
         
        @type save: boolean
        @param save: If True, the edited file will be saved on exit.

        @type filename: string
        @param filename: The file name to save the buffer to 
        """

        # Exit using the Quit menu 
        try:
            gedit = ooldtp.context(self.name)
            try:
                quit_menu = gedit.getchild(self.MNU_QUIT)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The quit menu was not found."
            quit_menu.selectmenuitem()
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "Mmm, something went wrong when closing the application."

        response = ldtp.waittillguiexist(self.QUESTION_DLG, '', 20)
    
        # If the text has changed, the save dialog will appear
        if response == 1:
            try:
                question_dialog = ooldtp.context(self.QUESTION_DLG)
            except ldtp.LdtpExecutionError:
                raise ldtp.LdtpExecutionError, "The Gedit question dialog was not found."
            
            # Test if the file needs to be saved
            if save:
                try:
                    question_dlg_btn_save = question_dialog.getchild(self.QUESTION_DLG_BTN_SAVE)
                    question_dlg_btn_save.click()
                except ldtp.LdtpExecutionError:
                    # If the Save button was not found, we will try to find the Save As
                    try:
                        question_dlg_btn_save = question_dialog.getchild(self.QUESTION_DLG_BTN_SAVE_AS)
                        question_dlg_btn_save.click()
                    except ldtp.LdtpExecutionError:
                        raise ldtp.LdtpExecutionError, "The save or save as buttons in Gedit question dialog were not found."

                    try:
                        ldtp.waittillguiexist(self.SAVE_DLG)
                        save_dialog = ooldtp.context(self.SAVE_DLG)
                    except ldtp.LdtpExecutionError:
                        raise ldtp.LdtpExecutionError, "The Gedit save dialog was not found."
                    try:
                        save_dlg_txt_filename = save_dialog.getchild(self.SAVE_DLG_TXT_NAME)
                    except ldtp.LdtpExecutionError:
                        raise ldtp.LdtpExecutionError, "The filename txt field in Gedit save dialog was not found."
                    try:
                        ldtp.wait(2)
                        save_dlg_txt_filename.settextvalue(filename)
                    except ldtp.LdtpExecutionError:
                        raise ldtp.LdtpExecutionError, "There was an error when writing the text."

                    try:
                        save_dlg_btn_save = save_dialog.getchild(self.SAVE_DLG_BTN_SAVE)
                    except ldtp.LdtpExecutionError:
                        raise ldtp.LdtpExecutionError, "The save button in Gedit save dialog was not found."
        
                    try:
                        save_dlg_btn_save.click()
                    except ldtp.LdtpExecutionError:
                        raise ldtp.LdtpExecutionError, "There was an error when pushing the Save button."

                    ldtp.waittillguinotexist(self.SAVE_DLG)
            
            else:
                try:
                    question_dlg_btn_close = question_dialog.getchild(self.QUESTION_DLG_BTN_CLOSE)
                    question_dlg_btn_close.click()
                except ldtp.LdtpExecutionError:
                    raise ldtp.LdtpExecutionError, "It was not possible to click the close button."

            response = ldtp.waittillguinotexist(self.name, '', 20)
 
class PolicyKit(Application):
    """
    PolicyKit class manages the GNOME pop up that ask for password for admin activities.
    """
    WINDOW     = "dlg0"
    TXT_PASS   = "txtPassword"
    BTN_OK     = "btnOK"
    BTN_CANCEL = "btnCancel"


    def __init__(self, password):
        """
        UpdateManager class main constructor
        
        @type password: string
        @param password: User's password for administrative tasks.

        """
        Application.__init__(self)
        self.password = password
    
    def wait(self):
        """
        Wait for the pop up window asking for the password to appear.

        @return 1, if the gksu window exists, 0 otherwise.
        """
        return ldtp.waittillguiexist(self.name)
        
    def set_password(self):
        """
        It enters the password in the text field and clicks enter. 
        """
        
        ooldtp.context(self.name)
        
        try:
            ldtp.enterstring (self.password)
            ldtp.enterstring ("<enter>")
            
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The PolicyKit txt field for the password was not found."
   
# TODO: Change this to use ooldtp
#        try:
#            btnOK = polKit.getchild(self.BTN_OK)
#        except ldtp.LdtpExecutionError, msg:
#            raise ldtp.LdtpExecutionError, "The GtkSudo OK button was not found."
#          
#        btnOK.click()
    
        #This also have problems because of the lack of accesibiliy information
        #ldtp.waittillguinotexist (self.name)
        
    def cancel(self):
        polKit = ooldtp.context(self.name)

        try:
            cancelButton = polKit.getchild(self.BTN_CANCEL)
        except ldtp.LdtpExecutionError:
            raise ldtp.LdtpExecutionError, "The PolicyKit cancel button was not found."
          
        cancelButton.click()
        ldtp.waittillguinotexist (self.name)
        

        
    
