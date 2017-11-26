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
  key = Key(config.key_email)

  newfile.encrypt(newfile.path + '.enc', key)
  time.sleep(2)
  newfile.decrypt(newfile.path + '.enc')

  
