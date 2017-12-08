import logging as log
import yaml

class Status(object):
    def __init__(self, config):
        # Config coming from the syncer
        self.config = config
        # Data for the local, decrypted, folders
        self.dec_folders = {}
        # Data for the remote, encrypted, counterparts of our folders
        self.enc_folders = {}


    def add_folder(self, path):
        self.dec_folders[path] = {}

    def add_file(self, path, file, timestamp):
        self.dec_folders[path][file] = {}
        self.dec_folders[path][file]['file_timestamp'] = timestamp

    def add_encrypted_path(self, path, file, encrypted_path):
        self.dec_folders[path][file]['encrypted_path'] = encrypted_path

    def add_encrypted_file_timestamp(self, path, file, timestamp):
        self.dec_folders[path][file]['encrypted_file_timestamp'] = timestamp

    def get_objects(self):
        return self.dec_folders

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
