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
from privd_syncer import Syncer as Syncer


if __name__ == "__main__":
  config = Config()

  key = Key(config.key_email)

  syncer = Syncer(config, key)
  
