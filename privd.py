# TODO:
# load, create and/or correct gpg keys

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
    parser.add_argument('-a', '--auto', help='Automatically syncs folders configured', required=False, action='store_true')
    parser.add_argument('-l', '--loop', help='Daemon-like run. Similar to auto but on a loop', required=False, action='store_true')
    parser.add_argument('-e', '--encrypt', help='Encrypt the folders configured', required=False, action='store_true')
    parser.add_argument('-d', '--decrypt', help='Decrypt the folders configured', required=False, action='store_true')

    args = vars(parser.parse_args())

    if args['verbose']:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)

    config = Config()
    key = Key(config.key_email)

    if args['encrypt']:
        # either syncer init initializes folders, or syncer.encrypt does
        syncer = Syncer(config, key)
        for folder in config.folders:
            syncer.folder_encrypt(folder['path'], config.enc_mainfolder, key)
    elif args['decrypt']:
        # either syncer init initializes folders, or syncer.encrypt does
        syncer = Syncer(config, key)
        for folder in config.folders:
            syncer.folder_decrypt(folder['path'], config.enc_mainfolder, key)
    elif args['auto']:
        # either syncer init initializes folders, or syncer.encrypt does
        syncer = Syncer(config, key)
        syncer.auto()
    elif args['loop']:
        # either syncer init initializes folders, or syncer.encrypt does
        syncer = Syncer(config, key)
        while True:
            syncer.auto()
            syncer.refresh()
            time.sleep(5)
  
