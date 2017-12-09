import logging as log
import yaml
from tools import get_hash as hash
from tools import get_timestamp as tstamp

class Status(object):
    def __init__(self, config):
        # Config coming from the syncer
        self.config = config
        # Data for the local, decrypted, folders
        # Changes go on this one, and we overwrite statusfile with it
        self.dec_folders = {}
        # Data for the remote, encrypted, counterparts of our folders
        # Only used for reference on what is in remote
        self.enc_folders = {}


    def add_folder(self, path):
        self.dec_folders[path] = {}

    def add_file(self, path, file):
        self.dec_folders[path][file] = {}
        self.dec_folders[path][file]['file_timestamp'] = tstamp(file)
        self.dec_folders[path][file]['file_checksum'] = hash(file)

    def add_encrypted_file(self, path, file, encrypted_path):
        self.dec_folders[path][file]['encrypted_path'] = encrypted_path
        self.dec_folders[path][file]['encrypted_file_timestamp'] = tstamp(encrypted_path)
        self.dec_folders[path][file]['encrypted_file_checksum'] = hash(encrypted_path)

    def get_objects(self):
        return self.dec_folders

    def get_folder(self, file, folders):
        for folder in folders:
            if folder + "/" in file:
                return folder

    def write_statusfile(self):
        log.debug("Status file: " + self.config.statusfile_path)
        with open(self.config.statusfile_path, 'w') as outfile:
            yaml.dump(self.dec_folders, outfile, default_flow_style=False)


    def load_statusfile(self):
        try:
            with open(self.config.statusfile_path, 'r') as stream:
                try:
                    self.enc_folders = yaml.load(stream)
                except yaml.YAMLError as exc:
                    log.error(exc)
                    return("YAMLError")
        except FileNotFoundError:
            log.error("File " + self.config.statusfile_path + " does not exist")
            return("FileNotFoundError")

    def compare(self):
        files = []
        not_in_dec = []
        not_in_enc = []
        in_both = []

        for folder in self.dec_folders:
            for file in self.dec_folders[folder]:
                if file not in self.enc_folders[folder]:
                    not_in_enc.append(file)
                files.append(file)

        for folder in self.enc_folders:
            for file in self.enc_folders[folder]:
                if file not in files:
                    files.append(file)
                    not_in_dec.append(file)
                else:
                    in_both.append(file)

        return(files, not_in_dec, not_in_enc, in_both)
