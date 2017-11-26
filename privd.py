# TODO:
# create a file.encrypt and a file.decrypt 
# do everything on a folder
# load, create and/or correct gpg keys


# OBJECTS
# SourceFolder
# DestinationFolder
# File

import gnupg
import time
import subprocess
from privd_config import Config
from privd_keys import Key as Key
from privd_files import File as File


if __name__ == "__main__":
  newfile = File('/home/aaf/keepass2DB.kdbx')
  config = Config()
  keys = Key(config.keys_folder)

  newfile.encrypt(newfile.path + '.enc')
  time.sleep(2)
  newfile.decrypt(newfile.path + '.enc')

  
