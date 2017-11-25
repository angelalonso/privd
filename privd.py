# TODO:
# create a file.encrypt and a file.decrypt 
# do everything on a folder
# load, create and/or correct gpg keys


# OBJECTS
# SourceFolder
# DestinationFolder
# File

import gnupg
from privd_config import Config

class File(object):
  """ A file that is going to be encrypted, decrypted and synced
  """

  def __init__(self, path):
    """ Returns a File whose path is path
    """
    self.path = path

  def encrypt(self, key):
    """ Returns the path to the encrypted version of the file
    """
    
    return "come"
    
class Keys(object):
  """ The GPG keys we will use and reuse
  """
  def __init__(self, gpghome):
    """ Returns a File whose path is path
    """
    self.gpghome = gpghome
    # TODO: add pubring and secring names to config
    self.gpg = gnupg.GPG(binary='/usr/bin/gpg',
      homedir=self.gpghome,
      keyring='privd_pubring.gpg',
      secring='privd_secring.gpg')

  def create_key(self):
    self.key_input = self.gpg.gen_key_input(
      key_type='RSA',
      key_length=4096)

    self.key = self.gpg.gen_key(self.key_input)

  def get_fingerprint(self):
    # IS THIS NEEDED?
    # TODO: make sure only one key is there, needed to clean up?
    return self.gpg.list_keys()[0]['fingerprint']
    
  

if __name__ == "__main__":
  newfile = File('$HOME/blah')
  print(newfile.encrypt("blah"))
  config = Config()

  keys = Keys(config.keys_folder)
#  keys.create_key()
#  print(keys.key.fingerprint)
#  print(dir(keys))
#  print(dir(keys.gpg))
  print(keys.getfingerprint())

 # batch_key_input = gpg.gen_key_input(
 #   key_type='RSA',
 #   key_length=4096)

 # key = gpg.gen_key(batch_key_input)

 # fp = key.fingerprint


 # with open('/home/aaf/.privd/Priv_test_source/file.dec', 'rb') as f:
 #   status = keys.gpg.encrypt(f, keys.fingerprint(),
 #       output='/home/aaf/.privd/Priv_test_dest/file.dec.enc')
  
  encrypted_path = '/home/aaf/.privd/Priv_test_dest/file.dec.enc'
  decrypted_path = '/home/aaf/.privd/Priv_test_dest/file.dec'
  with open(encrypted_path, 'rb') as a_file:
    keys.gpg.decrypt_file(a_file, output=decrypted_path)

 # key = gpg.gen_key(input_data)
 # print (gpg.export_keys(key.fingerprint))
  
