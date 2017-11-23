# TODO:
# Load a config file
# If missing, create a template one (or have it ready)

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
    


if __name__ == "__main__":
  newfile = File('$HOME/blah')
  print(newfile.encrypt("blah"))
  config = Config()

  gpg = gnupg.GPG(homedir=config.main_folder)
  print(config.main_folder)

  with open('/home/aaf/.privd/Priv_test_source/file.dec', 'rb') as f:
    status = gpg.encrypt_file(
        f, recipients=['testgpguser@mydomain.com'],
        output='/home/aaf/.privd/Priv_test_dest/file.dec.enc')
 # key = gpg.gen_key(input_data)
 # print (gpg.export_keys(key.fingerprint))
  
