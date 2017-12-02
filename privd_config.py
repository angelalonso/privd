import os
import yaml
from privd_tools import correct_path as cpath

class Config(object):
    """ A config object containing all values required
          It reads from a file and sets default values for the missing ones
    """

    def __init__(self):
        with open("config.yaml", 'r') as stream:
            load = yaml.safe_load(stream)
        #MAIN FOLDER
        try:
            self.main_folder = cpath(load['main_folder'])
        except KeyError as exc:
            self.main_folder = os.environ['HOME'] + "/.privd"
        #MAIN FOLDER
        try:
            self.enc_folder = cpath(load['enc_folder'])
        except KeyError as exc:
            self.enc_folder = self.main_folder + "/enc"
        #KEY EMAIL
        try:
            self.key_email = load['key_email']
        except KeyError as exc:
            self.key_email = "default@privd.foo"
        #FOLDERS TO ENCRYPT
        try:
            self.folders = load['folders']
            for folder in self.folders:
              folder['path'] = cpath(folder['path'])

        except KeyError as exc:
            self.folders = []


        #KEYS FOLDER
        # NEEDED?
        try:
            self.keys_folder = self.main_folder + load['keys_folder']
        except KeyError as exc:
            self.keys_folder = self.main_folder + "/keys"
        # Check and create folders
#if not os.path.exists(directory):
#    os.makedirs(directory)


