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
    parser.add_argument('-e', '--encrypt', help='Encrypt the folders configured', required=False, action='store_true')
    parser.add_argument('-d', '--decrypt', help='Decrypt the folders configured', required=False, action='store_true')
    parser.add_argument('-a', '--auto', help='Automatically syncs folders configured', required=False, action='store_true')

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
            syncer.folder_encrypt(folder['path'], config.enc_folder, key)
    elif args['decrypt']:
        # either syncer init initializes folders, or syncer.encrypt does
        syncer = Syncer(config, key)
        for folder in config.folders:
            syncer.folder_decrypt(folder['path'], config.enc_folder, key)
    elif args['auto']:
        # either syncer init initializes folders, or syncer.encrypt does
        syncer = Syncer(config, key)
        for folder in config.folders:
            syncer.folder_encrypt(folder['path'], config.enc_folder, key)
            log.debug("Waiting a sec")
            time.sleep(1)
            syncer.folder_decrypt(folder['path'], config.enc_folder, key)
  
