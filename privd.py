#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-

# TODO:
# NEXTUP:
# Remove unused functions
# Create better different levels of logging messages (info, debug, error...)
# Save public, private keys on home directory
# load, create and/or correct gpg keys
# Add other modes encrypt, decrypt...? is this even needed?
import timeit
import signal

import argparse
import gnupg
import logging as log
import os
import subprocess
import time
from configs import Config
from keys import Key as Key
from status import Status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Show higher level of verbosity', required=False, action='store_true')
    parser.add_argument('-s', '--single', help='Run the sync algorythm once', required=False, action='store_true')

    args = vars(parser.parse_args())
    if args['verbose']:
        log.basicConfig(format="%(levelname)s: %(asctime)s %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
        
    config = Config()
    key = Key(config.key_email)
    status = Status(config, key)
    if args['single']:
        log.debug("New run at " + str(int(time.time())) + " - " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) )
        status.daemon()
    else:
        daemon = True
        while daemon == True:
            log.debug("New run at " + str(int(time.time())) + " - " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) )
            status.daemon()


            # BACKUP ONLY WHILE I TEST
            for folder in config.folders:
                folder_path = folder['path']
                backup_path = folder_path + ".backup"
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)
                cmd = 'rsync -av ' + folder_path + '/ ' + backup_path
                cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 
            TIMEOUT = 5
            try:
                for i in range(0, TIMEOUT):
                    time.sleep(1)
            except KeyboardInterrupt:
                daemon = False
        print("Exiting gracefully...")

