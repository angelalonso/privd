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
        if not os.path.isfile(self.config.statusfile_path):
            log.error("NO REMOTE FILE")
            self.create_remote_statusfile()
        else:
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
        self.update_remote()

## local functions

    def get_local(self):
        for sync_folder in self.config.folders:
            self.register_local_folder(sync_folder)


    def update_local(self):
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            objects = glob.glob(sync_folder_path + "/**/*", recursive=True)

            registered_set = self.get_local_files_w_state(sync_folder_path, ('exists', 'recreated'))
            object_set = set()
            for obj in objects:
                if os.path.isfile(obj):
                    object_set.add(obj)
            # Set deleted objects as deleted
            for obj in registered_set - object_set:
                self.delete_local_file(sync_folder_path, obj)
            # Set exists or recreated objects as such
            for obj in object_set - registered_set:
                try: 
                    if self.local[sync_folder_path][obj]['state'] in ('deleted'):
                        self.recreate_local_file(sync_folder_path, obj)
                        # Necessary?
                    #else:
                    #    self.new_local_file(sync_folder_path, obj)
                except KeyError:
                    self.new_local_file(sync_folder_path, obj)
            # Check if updated, then Do something with updated files
            for obj in object_set.intersection(registered_set):
                if tstamp(obj) > self.local[sync_folder_path][obj]['local_file_timestamp']:
                    if not hash(obj) == self.local[sync_folder_path][obj]['local_file_checksum']:
                        log.debug(obj + " has changed contents locally")
                        self.set_local_file_record(sync_folder_path, obj, '')
                    else:
                        log.debug(obj + " has been updated locally but did not change")

            log.debug("## Local files marked as EXISTING  ##")
            log.debug(self.get_local_files_w_state(sync_folder_path, ('exists')))
            log.debug("## Local files marked as DELETED   ##")
            log.debug(self.get_local_files_w_state(sync_folder_path, ('deleted')))
            log.debug("## Local files marked as RECREATED ##")
            log.debug(self.get_local_files_w_state(sync_folder_path, ('recreated')))


    def get_local_files_w_state(self, sync_folder_path, state):
        result = set()
        for file in self.local[sync_folder_path]:
            if self.local[sync_folder_path][file]['state'] in state:
                result.add(file)
        return result


    def register_local_folder(self, sync_folder):
        sync_folder_path = sync_folder['path']
        self.local[sync_folder_path] = {}
        objects = glob.glob(sync_folder_path + "/**/*", recursive=True) 
        for obj in objects:
            if os.path.isfile(obj):
                self.set_local_file_record(sync_folder_path, obj, 'exists')

        
    def set_local_file_record(self, sync_folder_path, local_file, state):
        if local_file not in self.local[sync_folder_path]:
            self.local[sync_folder_path][local_file] = {}
        # TODO: error if it does not exist maybe?
        self.local[sync_folder_path][local_file]['local_file_timestamp'] = tstamp(local_file)
        self.local[sync_folder_path][local_file]['local_file_checksum'] = hash(local_file)
        # Set no state to keep the same one
        if not state == '':
            self.local[sync_folder_path][local_file]['state'] = state

        
    def new_local_file(self, sync_folder_path, local_file): 
        self.set_local_file_record(sync_folder_path, local_file, 'exists')

        
    def delete_local_file(self, sync_folder_path, local_file): 
        self.set_local_file_record(sync_folder_path, local_file, 'deleted')
        
        
    def recreate_local_file(self, sync_folder_path, local_file): 
        self.set_local_file_record(sync_folder_path, local_file, 'recreated')
        
## remote functions

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


    def create_remote_statusfile(self):
        self.remote = {}
        for sync_folder in self.config.folders:
            self.remote[sync_folder['path']] = {}
        self.write_remote_statusfile()


    def write_remote_statusfile(self):
        log.debug("Writing to status file: " + self.config.statusfile_path)
        with open(self.config.statusfile_path, 'w') as outfile:
            yaml.dump(self.remote, outfile, default_flow_style=False)


    def update_remote(self):
        for sync_folder in self.config.folders:
            print("--------------------------")
#            sync_folder_path = sync_folder['path']
#            objects = glob.glob(sync_folder_path + "/**/*", recursive=True)
#
#            registered_set = self.get_local_files_w_state(sync_folder_path, ('exists', 'recreated'))
#            object_set = set()
#            for obj in objects:
#                if os.path.isfile(obj):
#                    object_set.add(obj)
#            # Set deleted objects as deleted
#            for obj in registered_set - object_set:
#                self.delete_local_file(sync_folder_path, obj)
#            # Set exists or recreated objects as such
#            for obj in object_set - registered_set:
#                try: 
#                    if self.local[sync_folder_path][obj]['state'] in ('deleted'):
#                        self.recreate_local_file(sync_folder_path, obj)
#                        # Necessary?
#                    #else:
#                    #    self.new_local_file(sync_folder_path, obj)
#                except KeyError:
#                    self.new_local_file(sync_folder_path, obj)
#            # Check if updated, then Do something with updated files
#            for obj in object_set.intersection(registered_set):
#                if tstamp(obj) > self.local[sync_folder_path][obj]['local_file_timestamp']:
#                    if not hash(obj) == self.local[sync_folder_path][obj]['local_file_checksum']:
#                        log.debug(obj + " has changed contents locally")
#                        self.set_local_file_record(sync_folder_path, obj, '')
#                    else:
#                        log.debug(obj + " has been updated locally but did not change")
#
#            log.debug("## Local files marked as EXISTING  ##")
#            log.debug(self.get_local_files_w_state(sync_folder_path, ('exists')))
#            log.debug("## Local files marked as DELETED   ##")
#            log.debug(self.get_local_files_w_state(sync_folder_path, ('deleted')))
#            log.debug("## Local files marked as RECREATED ##")
#            log.debug(self.get_local_files_w_state(sync_folder_path, ('recreated')))

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
