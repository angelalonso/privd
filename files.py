import hashlib
import logging as log
import os
import subprocess
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome
from tools import enc_homefolder
from tools import get_encrypted_file_path

class File(object):
    """ A file object capable of being encrypted, decrypted and synced
    """
    def __init__(self, path):
        """ Returns a File whose path is path
        """
        self.path = getrealhome(path)


    def encrypt(self, file, config):
        """ Encrypts the file to a given file
            using gpg directly on bash
        """
        # This overcomplication is only here so that I can use $HOME on Mac and Linux
        real_file_enc_path = getrealhome(get_encrypted_file_path(file, config))
        log.debug("encrypting " + real_file_enc_path)
        os.makedirs(os.path.dirname(real_file_enc_path), exist_ok=True)
        try:
            os.remove(real_file_enc_path)
            log.debug("Had to remove previous " + real_file_enc_path)
        except FileNotFoundError: pass
        cmd = 'gpg -e -r ' + config.key.id + ' --trust-model always --output ' + real_file_enc_path + ' ' + self.path
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 
        for i in range(100000):
            enc_done = os.path.isfile(real_file_enc_path)
            if enc_done:
                break
            else:
                continue


    def decrypt(self, file_enc, config): 
        """ Decrypts file back to original path
        """
        real_file_enc_path = get_encrypted_file_path(file_enc, config)
        log.debug("decrypting from " + real_file_enc_path)
        log.debug("decrypting to " + self.path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            os.remove(self.path)
            log.debug("Had to remove previous " + self.path)
        except FileNotFoundError: pass
        cmd = 'gpg -d -o ' + self.path + ' ' + real_file_enc_path
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 
        for i in range(100000):
            dec_done = os.path.isfile(self.path)
            if dec_done:
                break
            else:
                continue
