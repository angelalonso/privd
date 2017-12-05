import os
import logging as log
import yaml
from privd_tools import correct_path as cpath

#TODO: Store paths with $HOME, use cpath ONLY when accessing the files and folders themselves!

class Config(object):
    """ A config object containing all values required
          It reads from a file and sets default values for the missing ones
    """

    def __init__(self):
        log.debug("Config files initiated:")
        with open("config.yaml", 'r') as stream:
            load = yaml.safe_load(stream)

        try:
            self.main_folder = cpath(load['main_folder'])
        except KeyError as exc:
            self.main_folder = os.environ['HOME'] + "/.privd"
            log.debug("Using default Main folder")
        log.debug("Main folder: " + self.main_folder)

        try:
            self.enc_folder = cpath(load['enc_folder'])
        except KeyError as exc:
            self.enc_folder = self.main_folder + "/enc"
            log.debug("Using default folder for encrypted files")
        log.debug("Folder for encrypted files: " + self.enc_folder)

        try:
            self.folders = load['folders']
            for folder in self.folders:
              folder['path'] = cpath(folder['path'])
        except KeyError as exc:
            self.folders = []
            log.debug("Empty set of Folders to encrypt")
        log.debug("Folders to encrypt: " + str(self.folders))

        try:
            self.key_email = load['key_email']
        except KeyError as exc:
            self.key_email = "default@privd.foo"
            log.debug("Using default E-Mail for GPG Key")
        log.debug("E-Mail for GPG Key: " + self.key_email)

        try:
            self.status_folder = load['status_folder']
        except KeyError as exc:
            self.status_folder = self.main_folder
            log.debug("Using default folder for the status file")
        try:
            self.status_file = load['status_file']
        except KeyError as exc:
            self.status_file = ".status"
            log.debug("Using default filename for status file")
        self.status_file_path = cpath(self.status_folder + "/" + self.status_file)
        log.debug("Status file: " + self.status_file_path)
