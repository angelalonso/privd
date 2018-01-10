#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-

import logging as log
import os
import shutil
import yaml
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome


class Config(object):
    """ A config object containing all values required
    It reads from a file and sets default values for the missing ones
    """
    def __init__(self):
        log.debug("Config files initiated:")
        try:
            with open(os.path.dirname(os.path.realpath(__file__)) + "/config.yaml", 'r') as stream:
                load = yaml.safe_load(stream)
        except FileNotFoundError:
            load = {}
            load['mainfolder'] = "$HOME/Dropbox/.privd"

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


    def export_file(self, path):
        """ Copies config.yaml to a given folder
        """
        log.debug("Exporting config file")
        shutil.copyfile("config.yaml", path + "/config.yaml")


    def import_file(self, path):
        """ Copies config.yaml from a given folder
        """
        log.debug("Importing config file")
        shutil.copyfile(path + "/config.yaml", "config.yaml")
