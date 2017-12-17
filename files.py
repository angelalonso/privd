import hashlib
import logging as log
import os
import subprocess
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome
from tools import enc_homefolder

class File(object):
    """ A file object capable of being encrypted, decrypted and synced
    """
    def __init__(self, path):
        """ Returns a File whose path is path
        """
        self.path = getrealhome(path)

    def encrypt(self, file_enc, config):
        """ Encrypts the file to a given file
            using gpg directly on bash
        """
        # This overcomplication is only here so that I can use $HOME on Mac and Linux
        real_file_enc_path = enc_homefolder(config, file_enc)
        # TODO: pass user and encryption details as a parameter 

        # whatever there is, remove it first
        log.debug("encrypting " + getrealhome(file_enc))
        os.makedirs(os.path.dirname(real_file_enc_path), exist_ok=True)
        try:
            os.remove(real_file_enc_path)
            log.debug("Had to remove previous " + real_file_enc_path)
        except FileNotFoundError: pass
        cmd = 'gpg -e -r ' + config.key.id + ' --trust-model always --output ' + real_file_enc_path + ' ' + self.path
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 


    def decrypt(self, file_enc, config):
        """ Decrypts file back to original path
        """
        real_file_enc_path = enc_homefolder(config, file_enc)
        log.debug("decrypting to " + self.path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            os.remove(self.path)
            log.debug("Had to remove previous " + self.path)
        except FileNotFoundError: pass
        cmd = 'gpg -d -o ' + self.path + ' ' + real_file_enc_path
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 

# REMOVE?
#    def statuscheck(self):
#        """ Gets the checksum  and last modification time of the file 
#
#        Hashlib part taken from https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
#        """
#        # We'll read in 64kb chunks
#        BUF_SIZE = 65536
#
#        # MD5? SHA1? why not both?
#        md5 = hashlib.md5()
#        sha1 = hashlib.sha1()
#
#        try:
#            with open(self.path, 'rb') as f:
#                while True:
#                    data = f.read(BUF_SIZE)
#                    if not data:
#                        break
#                    md5.update(data)
#                    sha1.update(data)
#            log.debug("MD5: {0}".format(md5.hexdigest()))
#            log.debug("SHA1: {0}".format(sha1.hexdigest()))
#            stats_buffer = os.stat(self.path)
#            log.debug("Last modified: {}".format(stats_buffer.st_mtime))
#        except FileNotFoundError:
#            log.debug("File " + self.path + " does not exist")
#        except IsADirectoryError:
#            log.debug("File " + self.path + " is a directory")
#
#
#
#
