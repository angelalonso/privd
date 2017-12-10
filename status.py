import glob
import logging as log
import os
import yaml
from tools import get_encrypted_file_path as enc_path
from tools import get_hash as hash
from tools import get_timestamp as tstamp

class Status(object):
    def __init__(self, config):
        # Config coming from the syncer
        self.config = config
        # Data for the local folders, new format
        self.local = {}
        self.get_local()
        self.get_remote()
        # TODO: remove both below
        # Data for the local, decrypted, folders
        # Changes go on this one, and we overwrite statusfile with it
        self.dec_folders = {}
        # Data for the remote, encrypted, counterparts of our folders
        # Only used for reference on what is in remote
        self.enc_folders = {}



######################## NEW FOR daemon and new status files and dicts
# TODO: use sync_folder instead of path everywhere, call them snyc_folders in config.yaml

    def refresh(self):
        self.update_local()
        self.get_remote()


    def get_local(self):
        for sync_folder in self.config.folders:
            self.register_local_folder(sync_folder)


    def update_local(self):
        # TODO:
        # Look for changes, new files, deleted files
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            objects = glob.glob(sync_folder['path'] + "/**/*", recursive=True)

            all_files = []
            object_list = []
            #print("#### REAL FILES:")
            for obj in objects:
                if os.path.isfile(obj):
                    object_list.append(obj)
            registered_list = set(self.local[sync_folder_path])
            print("#### LOCAL FILES:")
            print(object_list)
            print("#### REGISTERED FILES:")
            print(registered_list)
            # https://stackoverflow.com/questions/1319338/combining-two-lists-and-removing-duplicates-without-removing-duplicates-in-orig



    def get_remote(self):
        try:
            with open(self.config.statusfile_path, 'r') as stream:
                try:
                    self.remote = yaml.load(stream)
                except yaml.YAMLError as exc:
                    log.error(exc)
                    return("YAMLError")
        except FileNotFoundError:
            log.error("File " + self.config.statusfile_path + " does not exist")
            return("FileNotFoundError")


    def register_local_folder(self, sync_folder):
        sync_folder_path = sync_folder['path']
        self.local[sync_folder_path] = {}
        objects = glob.glob(sync_folder['path'] + "/**/*", recursive=True) 
        for obj in objects:
            if os.path.isfile(obj):
                self.set_local_file_record(sync_folder_path, obj, 'exists')
    

    def set_local_file_record(self, sync_folder_path, local_file, state):
        if local_file not in self.local[sync_folder_path]:
            self.local[sync_folder_path][local_file] = {}
        self.local[sync_folder_path][local_file]['local_file_timestamp'] = tstamp(local_file)
        self.local[sync_folder_path][local_file]['local_file_checksum'] = hash(local_file)
        self.local[sync_folder_path][local_file]['state'] = state

        
######################## END OF NEW

    def add_folder(self, path):
        self.dec_folders[path] = {}

    def add_file(self, path, file):
        if file not in self.dec_folders[path]:
            self.dec_folders[path][file] = {}
        self.dec_folders[path][file]['file_timestamp'] = tstamp(file)
        self.dec_folders[path][file]['file_checksum'] = hash(file)
        encrypted_path = enc_path(file, self.config, path)
        self.dec_folders[path][file]['encrypted_path'] = encrypted_path
        self.dec_folders[path][file]['encrypted_file_timestamp'] = tstamp(encrypted_path)
        self.dec_folders[path][file]['encrypted_file_checksum'] = hash(encrypted_path)

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
        log.debug("Writing to status file: " + self.config.statusfile_path)
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
                    if self.enc_folders[folder][file]['encrypted_file_timestamp'] == '':
                        not_in_enc.append(file)
                    else:
                        in_both.append(file)

        return(files, not_in_dec, not_in_enc, in_both)
