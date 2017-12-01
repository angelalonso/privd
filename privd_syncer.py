import subprocess
import os
import glob

class Syncer(object):
  """ A syncer object which contains:
  folders to be encrypted
  details about the encryption
  details to identify newer versions -> Moved to Files maybe?
  """

  def __init__(self, config):
    """ Returns a File whose path is path
    """
    for folder in config.folders:
      self.folder_initialize(folder['path'])
      self.folder_encrypt(folder['path'])

  def folder_initialize(self, path):
    if not os.path.exists(path):
      os.makedirs(path)
    elif os.path.isfile(path):
      print("Error! Folder name " + path + " already exists and it's a file")

  def folder_encrypt(self, path):
    objects = glob.glob(path + "/**/*", recursive=True)

    for obj in objects:
      if os.path.isfile(obj):
        # encrypt the shit out of it
        # Check data, store it into a file AND an object
        #   - hash
        #   - last modified
        print(obj)




