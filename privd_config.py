import os
import yaml

class Config(object):
    """ A config object containing all values required
          It reads from a file and sets default values for the missing ones
    """

    def __init__(self):
        with open("config.yaml", 'r') as stream:
            load = yaml.safe_load(stream)
        #MAIN FOLDER
        try:
            self.main_folder = load['main_folder'].replace('$HOME', os.environ['HOME'])
        except KeyError as exc:
            self.main_folder = os.environ['HOME'] + "/.privd"
        #KEYS FOLDER
        try:
            self.keys_folder = self.main_folder + load['keys_folder']
        except KeyError as exc:
            self.keys_folder = self.main_folder + "/keys"
        # Check and create folders
#if not os.path.exists(directory):
#    os.makedirs(directory)


