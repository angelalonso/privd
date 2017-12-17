# TODO:
# NEXTUP:
# Remove unused functions
# Create better different levels of logging messages (info, debug, error...)
# Save public, private keys on home directory
# load, create and/or correct gpg keys
# Add other modes encrypt, decrypt...? is this even needed?

import argparse
import gnupg
import logging as log
import time
import subprocess
from configs import Config
from keys import Key as Key
from syncers import Syncer as Syncer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Show higher level of verbosity', required=False, action='store_true')

    args = vars(parser.parse_args())
    if args['verbose']:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)

    config = Config()
    key = Key(config.key_email)

    syncer = Syncer(config, key)
    while True:
        log.debug("")
        log.debug(str(int(time.time())) + " - " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) )
        syncer.daemon()
        time.sleep(1)
  
