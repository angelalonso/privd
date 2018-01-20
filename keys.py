#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-

import gnupg
from gui import MyGUI as Gui
import logging as log
import subprocess
import os
""" Class to manage keys used for encryption and decryption
I'm using bash directly, 
because the gnupg library does not seem to produce proper decryptable files for binary files

"""
# TODO: create typical functions too: delete, list...
class Key(object):
    """ The GPG keys we will use and reuse
    """
    def __init__(self, key_email, gui):
        """ Returns a File whose path is path
        """
        self.id = key_email

        #checkcmd = 'gpg --list-keys ' + self.id + ' 2>/dev/null | grep pub'
        checkcmd = 'gpg --list-keys ' + self.id + ' | grep pub'
        try:
            subprocess.check_output([checkcmd], shell=True)
            gui.debug('Key FOUND')
        except subprocess.CalledProcessError as e:
            #TODO: ask user for confirmation before we create it?
            #log.debug('Key NOT found. Generating...')
            self.create_key()
            gui.debug('Key NOT found.')


    def create_key(self):
        """ This creates the GPG keys we will use and reuse
        """
        # Somehow, I cannot directly pass a string
        key_config = 'Key-Type: RSA\n Key-Length: 4096\n Name-Real: Privd Key\n Name-Email: ' + self.id + '\n Expire-Date: 0'
        key_config_file = './key.config'
        key_config_buffer = open(key_config_file,"w")
        key_config_buffer.write(key_config)
        key_config_buffer.close()

        cmd = 'sudo rngd -r /dev/urandom && gpg --batch --gen-key ' + key_config_file 
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True).wait()

        # Clean up afterwards 
        os.remove(key_config_file)


    def export_all(self, path):
        """ This exports keys to the folder indicated
        """
        cmd = 'gpg --export -a "' + self.id + '" > ' + path + '/key.pub'
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        cmd = 'gpg --export-secret-key -a "' + self.id + '" > ' + path + '/key.priv'
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)

    def import_all(self, path):
        """ This imports keys from the folder indicated
        """
        cmd = 'gpg --import ' + path + '/key.pub'
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        cmd = 'gpg --import ' + path + '/key.priv'
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)

