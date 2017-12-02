import subprocess
import os

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
    os.remove(file_enc)
    cmd = 'gpg -e -r ' + key.id + ' --trust-model always --output ' + file_enc + ' ' + self.path
    cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 


  def decrypt(self, file_enc):
    """ Decrypts file back to original path
    """
    #cmd = 'gpg -d --output ' + self.path + '.dec ' + file_enc
    cmd = 'gpg -d -o ' + self.path + ' ' + file_enc
    cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 
    
