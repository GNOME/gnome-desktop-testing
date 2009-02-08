"""
This is the "gnome" module.

The gnome module provides wrappers for LDTP to make the write of Gnome tests easier. 
"""
from ooldtp import *
from ldtp import *
from ldtputils import *
import gnome_constants
from time import *
from re import *

def open_and_check_app(app_name, window_title_txt):
    """
    Given an application, it tries to open it.
     
    @type app_name: string
    @param app_name: The command to start the application.
    
    @type window_title_txt: string 
    @param window_title_txt: The name of the window to recognize once opened.
        
        The naming convention is the following:
        
        E{-} Prepend 'frm' if the window is a form, or 'dlg' if the window is a dialog.
        
        E{-} Append the window name with no spaces.
              
        Example: For the window Disk Usage Analyzer, the window name would be frmDiskUsageAnalyzer.
    
    """
    
    launchapp(app_name)

    wait(2)
    response = waittillguiexist(window_title_txt, '', 20)
    
    if response == 0:
        raise LdtpExecutionError, "The " + window_title_txt + " window was not found."    

class Application:
    """
    Supperclass for the rest of the applications
    """
    def __init__(self, name = ""):
        self.name = name
      
    def remap(self):
        """
        It reloads the application map for the given context.
        """
        remap(self.name)

    def exit(self, close_type='menu', close_name='mnuQuit'):
        """
        Given an application, it tries to quit it.
         
        @type close_type: string
        @param close_type: The type of close widget of the application. Types: menu, button.
        @type close_name: string
        @param close_name: The name of the exit widget of the application. If not mentioned the default will be used ("Quit").
        """
        try:
            app = context(self.name)
            try:
                close_widget = app.getchild(close_name)
            except LdtpExecutionError, msg:
                raise LdtpExecutionError, "The " + close_name + " widget was not found."

            if close_type == 'menu':
                close_widget.selectmenuitem()
            elif close_type == 'button':
                close_widget.click()
            else:
                raise LdtpExecutionError, "Wrong close item type."
            response = waittillguinotexist(self.name, '', 20)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "Mmm, something went wrong when closing the application: " + str(msg)

    def save(self, save_menu='mnuSave'):
        """
        Given an application, it tries to save the current document. 
        This method gives very basic functionality. Please, override this method in the subclasses for error checking.
         
        @type save_menu: string
        @param save_menu: The name of the Save menu of the application. If not mentioned the default will be used ("Save").
        """
        try:
            app = context(self.name)
            try:
                actualMenu = app.getchild(save_menu)
            except LdtpExecutionError, msg:
                raise LdtpExecutionError, "The " + save_menu + " menu was not found."

            actualMenu.selectmenuitem()
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "Mmm, something went wrong when saving the current document:" + str(msg)

    def write_text(self, text, txt_field=''):
        """
        Given an application it tries to write text to its current buffer.
        """
        app = context(self.name)

        if txt_field == '':
            try:
                enterstring(text)
            except LdtpExecutionError, msg:
                raise LdtpExecutionError, "We couldn't write text: " + str(msg)
        else:
            try:
                app_txt_field = app.getchild(txt_field)
            except LdtpExecutionError, msg:
                raise LdtpExecutionError, "The " + txt_field + " text field was not found: " + str(msg)
            try:
                app_txt_field.settextvalue(text)
            except LdtpExecutionError, msg:
                raise LdtpExecutionError, "We couldn't write text: " + str(msg)

class Seahorse(Application):
    """
    Seahorse manages the Seahorse application.
    """
 
    def __init__(self):
        Application.__init__(self, gnome_constants.SH_WINDOW)

    def open(self):
        open_and_check_app(gnome_constants.SH_LAUNCHER, gnome_constants.SH_WINDOW)

    def new_key(self, key_type):
        
        seahorse = context(self.name)
        
        try:
            mnu_new_key = seahorse.getchild(gnome_constants.SH_MNU_NEWKEY)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The new key menu was not found: " + str(msg)

        try:
            mnu_new_key.selectmenuitem() 
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "There was a problem when selecting new key menu item: " + str(msg)

        try:
            waittillguiexist(gnome_constants.SH_NEWKEY_DLG)
            dlg_new_key = context(gnome_constants.SH_NEWKEY_DLG)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The new key dialog was not found: " + str(msg)

        try:
            table  = dlg_new_key.getchild(role = 'table')
            types_table = table[0]

            for i in range(0, types_table.getrowcount(), 1):
                text = types_table.getcellvalue(i, 1)
                candidate = text.split('\n')[0]
                if candidate == key_type:
                    types_table.selectrowindex(i)
                    break
                wait(1)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "Error getting the key types table: " + str(msg)

        try:
            btn_continue = dlg_new_key.getchild(gnome_constants.SH_BTN_CONTINUE)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The continue button at the new key dialog was not found: " + str(msg)

        try:
            btn_continue.click() 
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "There was a problem when clicking the continue button: " + str(msg)
        
    def new_pgp_key(self, full_name, email, comment, passphrase):
        
        self.new_key(gnome_constants.SH_TYPE_PGP)

        try:
            waittillguiexist(gnome_constants.SH_NEWPGP_DLG)
            dlg_new_pgp = context(gnome_constants.SH_NEWPGP_DLG)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The new key dialog was not found: " + str(msg)

        try:
            txt_field = dlg_new_pgp.getchild(gnome_constants.SH_DLG_NEWPGP_FULLNAME)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The " + txt_field + " text field was not found: " + str(msg)
        try:
            txt_field.settextvalue(full_name)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "We couldn't write text: " + str(msg)

        try:
            txt_field = dlg_new_pgp.getchild(gnome_constants.SH_DLG_NEWPGP_EMAIL)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The " + txt_field + " text field was not found: " + str(msg)
        try:
            txt_field.settextvalue(email)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "We couldn't write text: " + str(msg)
   
        try:
            txt_field = dlg_new_pgp.getchild(gnome_constants.SH_DLG_NEWPGP_COMMENT)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The " + txt_field + " text field was not found: " + str(msg)
        try:
            txt_field.settextvalue(comment)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "We couldn't write text: " + str(msg)

        try:
            btn_create = dlg_new_pgp.getchild(gnome_constants.SH_BTN_NEWPGP_CREATE)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The create button at the new PGP key dialog was not found: " + str(msg)

        try:
            btn_create.click() 
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "There was a problem when clicking the create button " + str(msg)
       
        try:
            waittillguiexist(gnome_constants.SH_DLG_NEWPGP_PASS)
            dlg_new_pgp_pass = context(gnome_constants.SH_DLG_NEWPGP_PASS)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The new pgp key passphrase dialog was not found: " + str(msg)

        try:
            enterstring(passphrase)
            enterstring("<tab>")
            enterstring(passphrase)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "Error entering passphrase" + str(msg)
 
        try:
            btn_pass_ok = dlg_new_pgp_pass.getchild(gnome_constants.SH_BTN_PASS_OK)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The OK button at the new PGP key passphrase dialog was not found: " + str(msg)

        try:
            btn_pass_ok.click() 
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "There was a problem when clicking the OK button " + str(msg)
 
        try:
            waittillguiexist(gnome_constants.SH_DLG_GENERATING_PGP)
            waittillguinotexist(gnome_constants.SH_DLG_GENERATING_PGP)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The new pgp generating key dialog was not found: " + str(msg)


class GEdit(Application):
    """
    GEdit manages the Gedit application.
    """
 
    def __init__(self):
        Application.__init__(self, gnome_constants.GE_WINDOW)

    def write_text(self, text):
        """
        It writes text to the current buffer of the Gedit window.

        @type text: string
        @param text: The text string to be written to the current buffer.
        """
        Application.write_text(self, text, gnome_constants.GE_TXT_FIELD)

    def save(self, filename):
        """
        It tries to save the current opened buffer to the filename passed as parameter.

        TODO: It does not manage the overwrite dialog yet.

        @type filename: string
        @param filename: The name of the file to save the buffer to.
        """
        Application.save(self)
        gedit = context(self.name)

        try:
            waittillguiexist(gnome_constants.GE_SAVE_DLG)
            save_dialog = context(gnome_constants.GE_SAVE_DLG)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The Gedit save dialog was not found: " + str(msg)
        try:
            save_dlg_txt_filename = save_dialog.getchild(gnome_constants.GE_SAVE_DLG_TXT_NAME)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The filename txt field in Gedit save dialog was not found: " + str(msg)
        try:
            wait(2)
            save_dlg_txt_filename.settextvalue(filename)
        except LdtpExecutionError, msg:
           raise LdtpExecutionError, "We couldn't write text: " + str(msg)

        try:
            save_dlg_btn_save = save_dialog.getchild(gnome_constants.GE_SAVE_DLG_BTN_SAVE)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The button Save in Gedit save dialog was not found: " + str(msg)
        
        try:
            save_dlg_btn_save.click()
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "There was an error when pushing the Save button: " + str(msg)

        waittillguinotexist(gnome_constants.GE_SAVE_DLG)
        
    def open(self):
        """
        It opens the gedit application and raises an error if the application
        didn't start properly.

        """
        open_and_check_app(gnome_constants.GE_LAUNCHER, gnome_constants.GE_WINDOW)

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
            gedit = context(self.name)
            try:
                actualMenu = gedit.getchild(gnome_constants.GE_MNU_QUIT)
            except LdtpExecutionError, msg:
                raise LdtpExecutionError, "The " + quit_menu + " menu was not found."
            actualMenu.selectmenuitem()
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "Mmm, something went wrong when closing the application: " + str(msg)

        response = waittillguiexist(gnome_constants.GE_QUESTION_DLG, '', 20)
    
        # If the text has changed, the save dialog will appear
        if response == 1:
            try:
                question_dialog = context(gnome_constants.GE_QUESTION_DLG)
            except LdtpExecutionError, msg:
                raise LdtpExecutionError, "The Gedit question dialog was not found: " + str(msg)
            
            # Test if the file needs to be saved
            if save:
                try:
                    question_dlg_btn_save = question_dialog.getchild(gnome_constants.GE_QUESTION_DLG_BTN_SAVE)
                    question_dlg_btn_save.click()
                except LdtpExecutionError, msg:
                    # If the Save button was not found, we will try to find the Save As
                    try:
                        question_dlg_btn_save = question_dialog.getchild(gnome_constants.GE_QUESTION_DLG_BTN_SAVE_AS)
                        question_dlg_btn_save.click()
                    except LdtpExecutionError, msg:
                        raise LdtpExecutionError, "The save or save as buttons in Gedit question dialog were not found: " + str(msg)

                    try:
                        waittillguiexist(gnome_constants.GE_SAVE_DLG)
                        save_dialog = context(gnome_constants.GE_SAVE_DLG)
                    except LdtpExecutionError, msg:
                        raise LdtpExecutionError, "The Gedit save dialog was not found: " + str(msg)
                    try:
                        save_dlg_txt_filename = save_dialog.getchild(gnome_constants.GE_SAVE_DLG_TXT_NAME)
                    except LdtpExecutionError, msg:
                        raise LdtpExecutionError, "The filename txt field in Gedit save dialog was not found: " + str(msg)
                    try:
                        wait(2)
                        save_dlg_txt_filename.settextvalue(filename)
                    except LdtpExecutionError, msg:
                        raise LdtpExecutionError, "We couldn't write text: " + str(msg)

                    try:
                        save_dlg_btn_save = save_dialog.getchild(gnome_constants.GE_SAVE_DLG_BTN_SAVE)
                    except LdtpExecutionError, msg:
                        raise LdtpExecutionError, "The save button in Gedit save dialog was not found: " + str(msg)
        
                    try:
                        save_dlg_btn_save.click()
                    except LdtpExecutionError, msg:
                        raise LdtpExecutionError, "There was an error when pushing the Save button: " + str(msg)

                    waittillguinotexist(gnome_constants.GE_SAVE_DLG)
            
            else:
                try:
                    question_dlg_btn_close = question_dialog.getchild(gnome_constants.GE_QUESTION_DLG_BTN_CLOSE)
                    question_dlg_btn_close.click()
                except LdtpExecutionError, msg:
                    raise LdtpExecutionError, "It was not possible to click the close button: " + str(msg)

            response = waittillguinotexist(self.name, '', 20)
 
class PolicyKit(Application):
    """
    PolicyKit class manages the GNOME pop up that ask for password for admin activities.
    """
    
    def __init__(self, password):
        """
        UpdateManager class main constructor
        
        @type password: string
        @param password: User's password for administrative tasks.

        """
        Application.__init__(self, gnome_constants.SU_WINDOW)
        self.password = password
    
    def wait(self):
        """
        Wait for the pop up window asking for the password to appear.

        @return 1, if the gksu window exists, 0 otherwise.
        """
        return waittillguiexist(gnome_constants.SU_WINDOW)
        
    def set_password(self):
        """
        It enters the password in the text field and clicks enter. 
        """
        
        polKit = context(gnome_constants.SU_WINDOW)
        
        try:
            enterstring (self.password)
            enterstring ("<enter>")
            
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The PolicyKit txt field for the password was not found."
   
# TODO: Change this to use ooldtp
#        try:
#            btnOK = polKit.getchild(gnome_constants.SU_BTN_OK)
#        except LdtpExecutionError, msg:
#            raise LdtpExecutionError, "The GtkSudo OK button was not found."
#          
#        btnOK.click()
    
        #This also have problems because of the lack of accesibiliy information
        #waittillguinotexist (gnome_constants.SU_WINDOW)
        
    def cancel(self):
        polKit = context(gnome_constants.SU_WINDOW)

        try:
            cancelButton = polKit.getchild(gnome_constants.SU_BTN_CANCEL)
        except LdtpExecutionError, msg:
            raise LdtpExecutionError, "The PolicyKit cancel button was not found."
          
        cancelButton.click()
        waittillguinotexist (gnome_constants.SU_WINDOW)
        

        
    
