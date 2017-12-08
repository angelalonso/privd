import glob
import logging as log
import os
import subprocess
import sys
import time

from files import File as File
from tools import get_timestamp as tstamp
from status import Status


class Syncer(object):
    """ A syncer object which contains:
    folders to be encrypted
    details about the encryption
    details to identify newer versions -> Moved to Files maybe?
    """

    def __init__(self, config, key):
        """ Returns a File whose path is path
        """
        self.config = config
        self.key = key

        self.status = Status(self.config)

        for folder in self.config.dec_folders:
            self.folder_initialize(folder['path'])

        if not os.path.isfile(self.config.statusfile_path):
            self.status.write_statusfile()


    def auto(self):

        self.status.load_statusfile()

        for folder in self.config.dec_folders:
            self.folder_encrypt(folder['path'], self.config.enc_mainfolder, self.key)
            log.debug("Waiting a sec")
            time.sleep(1)
            self.folder_decrypt(folder['path'], self.config.enc_mainfolder, self.key)


    def folder_initialize(self, path):
        if not os.path.exists(path):
            log.debug("Creating folder " + path)
            os.makedirs(path)
        elif os.path.isfile(path):
            log.debug("Error! Folder name " + path + " already exists and it's a file")
        self.status.add_folder(path)
        objects = glob.glob(path + "/**/*", recursive=True)
        for obj in objects:
            self.status.add_file(path, obj, tstamp(obj))


    def folder_encrypt(self, path, enc_mainfolder, key):
        objects = glob.glob(path + "/**/*", recursive=True)

        # Create the folder as such within the enc folder
        enc_path = path.replace(path, enc_mainfolder + path)
        if not os.path.exists(enc_path):
            log.debug("Creating folder " + enc_path)
            os.makedirs(enc_path)

        for obj in objects:
            self.status.add_file(path, obj, tstamp(obj))
            enc_obj_path = obj.replace(path, enc_mainfolder + path) + '.gpg'
            if os.path.isfile(obj):
                managed_file = File(obj)
                managed_file.encrypt(enc_obj_path, key)
                # This is needed because the encryption takes a bit. 100 is a random number really
                for i in range(1000):
                    try:
                        self.status.add_encrypted_path(path, obj, enc_obj_path)
                        self.status.add_encrypted_file_timestamp(path, obj, tstamp(enc_obj_path))
                    except FileNotFoundError:
                        continue
                    break
            elif os.path.isdir(obj):
                if not os.path.exists(enc_obj_path):
                    os.makedirs(enc_obj_path)
        self.status.write_statusfile()
        self.status.load_statusfile()


    def folder_decrypt(self, path, enc_mainfolder, key):
        objects = glob.glob(enc_mainfolder + path + "/**/*", recursive=True)
        log.debug(path)
        log.debug(enc_mainfolder)

        # Create the folder to decrypt file to if it isn't there already
        if not os.path.exists(path):
            log.debug("Creating folder " + path)
            os.makedirs(path)
        for obj in objects:
            log.debug(obj)
            dec_obj_path = obj.replace(enc_mainfolder + path, path).replace('.gpg','')
            log.debug(dec_obj_path)
            if os.path.isfile(obj):
                managed_file = File(dec_obj_path)
                managed_file.decrypt(obj)
            elif os.path.isdir(obj):
                if not os.path.exists(dec_obj_path):
                    os.makedirs(dec_obj_path)
      
