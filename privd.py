# TODO:
# load, create and/or correct gpg keys

import argparse
import gnupg
import logging as log
import time
import subprocess
from privd_config import Config
from privd_keys import Key as Key
from privd_syncer import Syncer as Syncer


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
  
