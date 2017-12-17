import os
import logging as log
import yaml
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome

#TODO: Store paths with $HOME, use real path ONLY when accessing the files and folders themselves!
# - change config to avoid this
# - adapt as it goes

class Config(object):
    """ A config object containing all values required
          It reads from a file and sets default values for the missing ones
    """

    def __init__(self):
        log.debug("Config files initiated:")
        with open("config.yaml", 'r') as stream:
            load = yaml.safe_load(stream)

        try:
            self.mainfolder = load['mainfolder']
        except KeyError as exc:
            self.mainfolder = os.environ['HOME'] + "/.privd"
            log.debug("Using default Main folder")
        log.debug("Main folder: " + self.mainfolder)

        try:
            self.enc_mainfolder = load['enc_mainfolder']
        except KeyError as exc:
            self.enc_mainfolder = self.mainfolder + "/enc"
            log.debug("Using default folder for encrypted files")
        log.debug("Folder for encrypted files: " + self.enc_mainfolder)

        try:
            self.folders = load['folders']
            for folder in self.folders:
              folder['path'] = folder['path']
        except KeyError as exc:
            self.folders = []
            log.debug("Empty set of Folders to encryptedly sync")
        log.debug("Folders to encrypt: " + str(self.folders))
        # TODO: remove these when the previous ones are ready:
        try:
            self.dec_folders = load['folders']
            for folder in self.dec_folders:
              folder['path'] = folder['path']
        except KeyError as exc:
            self.dec_folders = []
            log.debug("Empty set of Folders to encrypt")
        log.debug("Folders to encrypt: " + str(self.dec_folders))

        try:
            self.key_email = load['key_email']
        except KeyError as exc:
            self.key_email = "default@privd.foo"
            log.debug("Using default E-Mail for GPG Key")
        log.debug("E-Mail for GPG Key: " + self.key_email)

        try:
            self.status_folder = load['status_folder']
        except KeyError as exc:
            self.status_folder = self.mainfolder
            log.debug("Using default folder for the status file")
        try:
            self.statusfile = load['statusfile']
        except KeyError as exc:
            self.statusfile = ".status"
            log.debug("Using default filename for status file")
        self.statusfile_path = (self.status_folder + "/" + self.statusfile)
        log.debug("Status file: " + self.statusfile_path)
