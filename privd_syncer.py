import gc
import glob
import logging as log
import os
import subprocess
import time
import yaml

from privd_file import File as File

# TODO: create a class to store status
class Status(object):
    def __init__(self, statusfile):
        self.folders = {}
        self.statusfile_folders = {}
        self.statusfile = statusfile
        read_status_file()

    def add_folder(self, path):
        self.folders[path] = {}

    def add_file(self, path, file):
        self.folders[path][file] = {}

    def add_encrypted_path(self, path, file, encrypted_path):
        self.folders[path][file]['encrypted_path'] = encrypted_path

    def add_encrypted_file_timestamp(self, path, file, timestamp):
        self.folders[path][file]['encrypted_file_timestamp'] = timestamp

    def get_objects(self):
        return self.folders

    def write_status_file(self):
        log.debug("Status file: " + self.statusfile)
        with open(self.statusfile, 'w') as outfile:
            yaml.dump(self.folders, outfile, default_flow_style=False)

    def read_status_file(self):
        with open(self.statusfile, 'r') as stream:
            try:
                self.statusfile_folders = yaml.load(stream)
            except yaml.YAMLError as exc:
                log.error(exc)


class Syncer(object):
    """ A syncer object which contains:
    folders to be encrypted
    details about the encryption
    details to identify newer versions -> Moved to Files maybe?
    """

    def __init__(self, config, key):
        """ Returns a File whose path is path
        """
        self.status = Status(config.status_file_path)
        log.debug("Using " + config.status_file_path + " to keep track of files")
        for folder in config.folders:
            self.folder_initialize(folder['path'])


    def folder_initialize(self, path):
        if not os.path.exists(path):
            log.debug("Creating folder " + path)
            os.makedirs(path)
        elif os.path.isfile(path):
            log.debug("Error! Folder name " + path + " already exists and it's a file")
        self.status.add_folder(path)


    def folder_encrypt(self, path, enc_folder, key):
        objects = glob.glob(path + "/**/*", recursive=True)

        # Create the folder as such within the enc folder
        enc_path = path.replace(path, enc_folder + path)
        if not os.path.exists(enc_path):
            log.debug("Creating folder " + enc_path)
            os.makedirs(enc_path)

        for obj in objects:
            self.status.add_file(path, obj)
            enc_obj_path = obj.replace(path, enc_folder + path) + '.gpg'
            if os.path.isfile(obj):
                managed_file = File(obj)
                managed_file.encrypt(enc_obj_path, key)
                # This is needed because the encryption takes a bit. 100 is a random number really
                for i in range(1000):
                    try:
                        self.status.add_encrypted_path(path, obj, enc_obj_path)
                        self.status.add_encrypted_file_timestamp(path, obj, format(os.stat(enc_obj_path).st_mtime))
                    except FileNotFoundError:
                        continue
                    break
                # TODO:
                # Check data, store it into a file AND an object
                #   - hash
                #   - last modified
            elif os.path.isdir(obj):
                if not os.path.exists(enc_obj_path):
                    os.makedirs(enc_obj_path)
        log.debug("########################### TESTING" + path + " - " + obj)
        log.debug(self.status.get_objects())
        log.debug("########################### TESTING")
        self.status.write_status_file()
        self.status.read_status_file()



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
                log.debug("########################### TESTING" + path + " - " + obj)
                log.debug(self.status[path][obj]["encrypted_file"])
                log.debug(self.status[path][obj]["encrypted_file_timestamp"])
                log.debug("########################### TESTING")
            elif os.path.isdir(obj):
                if not os.path.exists(dec_obj_path):
                    os.makedirs(dec_obj_path)
      
