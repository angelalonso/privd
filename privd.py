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
  input_data = gpg.gen_key_input(key_type="RSA", key_length=1024)
  key = gpg.gen_key(input_data)
  gpg.export_keys(key.fingerprint)
