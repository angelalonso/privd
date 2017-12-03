import hashlib
import logging as log
import os
import subprocess

class File(object):
    """ A file object capable of being encrypted, decrypted and synced
    """
    # TODO: check that the file exists

    def __init__(self, path):
        """ Returns a File whose path is path
        """
        self.path = path

    def encrypt(self, file_enc, key):
        """ Encrypts the file to a given file
            using gpg directly on bash
        """
        # TODO: pass user and encryption details as a parameter 

        # whatever there is, remove it first
        log.debug("encrypting " + file_enc)
        self.statuscheck()
        try:
            os.remove(file_enc)
            log.debug("Had to remove previous " + file_enc)
        except FileNotFoundError: pass
        cmd = 'gpg -e -r ' + key.id + ' --trust-model always --output ' + file_enc + ' ' + self.path
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 


    def decrypt(self, file_enc):
        """ Decrypts file back to original path
        """
        log.debug("decrypting to " + self.path)
        self.statuscheck()
        try:
            os.remove(self.path)
            log.debug("Had to remove previous " + self.path)
        except FileNotFoundError: pass
        cmd = 'gpg -d -o ' + self.path + ' ' + file_enc
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 


    def statuscheck(self):
        """ Gets the checksum  and last modification time of the file 

        Hashlib part taken from https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
        """
        # We'll read in 64kb chunks
        BUF_SIZE = 65536

        # MD5? SHA1? why not both?
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()

        with open(self.path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                md5.update(data)
                sha1.update(data)

        log.debug("MD5: {0}".format(md5.hexdigest()))
        log.debug("SHA1: {0}".format(sha1.hexdigest()))

        stats_buffer = os.stat(self.path)
        log.debug("Last modified: {}".format(stats_buffer.st_mtime))



