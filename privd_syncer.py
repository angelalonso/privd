import glob
import logging as log
import os
import subprocess
import time

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


    def folder_initialize(self, path):
        if not os.path.exists(path):
            log.debug("Creating folder " + path)
            os.makedirs(path)
        elif os.path.isfile(path):
            log.debug("Error! Folder name " + path + " already exists and it's a file")


    def folder_encrypt(self, path, enc_folder, key):
        objects = glob.glob(path + "/**/*", recursive=True)

        # Create the folder as such within the enc folder
        enc_path = path.replace(path, enc_folder + path)
        if not os.path.exists(enc_path):
            log.debug("Creating folder " + enc_path)
            os.makedirs(enc_path)

        for obj in objects:
            enc_obj_path = obj.replace(path, enc_folder + path) + '.gpg'
            if os.path.isfile(obj):
                managed_file = File(obj)
                managed_file.encrypt(enc_obj_path, key)
                # TODO:
                # Check data, store it into a file AND an object
                #   - hash
                #   - last modified
            elif os.path.isdir(obj):
                if not os.path.exists(enc_obj_path):
                    os.makedirs(enc_obj_path)


    def folder_decrypt(self, path, enc_folder, key):
        objects = glob.glob(enc_folder + path + "/**/*", recursive=True)
        log.debug(path)
        log.debug(enc_folder)

        # Create the folder to decrypt file to if it isn't there already
        if not os.path.exists(path):
            log.debug("Creating folder " + path)
            os.makedirs(path)
        for obj in objects:
            log.debug(obj)
            dec_obj_path = obj.replace(enc_folder + path, path).replace('.gpg','')
            log.debug(dec_obj_path)
            if os.path.isfile(obj):
                managed_file = File(dec_obj_path)
                managed_file.decrypt(obj)
            elif os.path.isdir(obj):
                if not os.path.exists(dec_obj_path):
                    os.makedirs(dec_obj_path)
      
