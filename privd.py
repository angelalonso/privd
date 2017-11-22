# TODO:
# Load a config file
# If missing, create a template one (or have it ready)

# OBJECTS
# SourceFolder
# DestinationFolder
# File

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

