import subprocess
import os
import glob

from privd_file import File as File


class Syncer(object):
  """ A syncer object which contains:
  folders to be encrypted
  details about the encryption
  details to identify newer versions -> Moved to Files maybe?
  """

  def __init__(self, config, key):
    """ Returns a File whose path is path
    """
    for folder in config.folders:
      self.folder_initialize(folder['path'])
      self.folder_encrypt(folder['path'], config.enc_folder, key)
      self.folder_decrypt(folder['path'], config.enc_folder, key)

  def folder_initialize(self, path):
    if not os.path.exists(path):
      os.makedirs(path)
    elif os.path.isfile(path):
      print("Error! Folder name " + path + " already exists and it's a file")

  def folder_encrypt(self, path, enc_folder, key):
    objects = glob.glob(path + "/**/*", recursive=True)

    # Create the folder as such within the enc folder
    enc_path = path.replace(path, enc_folder + "/" + path)
    if not os.path.exists(enc_path):
      os.makedirs(enc_path)

    for obj in objects:
      enc_obj_path = obj.replace(path, enc_folder + "/" + path)
      if os.path.isfile(obj):
        managed_file = File(obj)
        # TODO: overwrite!
        managed_file.encrypt(enc_obj_path, key)
        # TODO:
        # Check data, store it into a file AND an object
        #   - hash
        #   - last modified
      elif os.path.isdir(obj):
        if not os.path.exists(enc_obj_path):
          os.makedirs(enc_obj_path)


  #TODO: do this actually
  # TODO: use better var names, check if overwrite or not, create dirs
  def folder_decrypt(self, path, enc_folder, key):
    objects = glob.glob(path + "/**/*", recursive=True)

    # Create the folder as such within the enc folder
    enc_path = path.replace(path, enc_folder + "/" + path)
    for obj in objects:
      enc_obj = obj.replace(path, enc_folder + "/" + path)
      dec_file = File(obj)
      dec_file.decrypt(enc_obj)
      
