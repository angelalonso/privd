import glob
import logging as log
import os
import time
import yaml
from files import File as File
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome
from tools import enc_homefolder
from tools import get_encrypted_file_path as enc_path
from tools import get_decrypted_file_path as dec_path
#from tools import get_hash as hash
from tools import checksum as hash
#from tools import get_timestamp as tstamp
from tools import timestamp as tstamp

class Status(object):
    def __init__(self, config):
        # Config coming from the syncer
        self.config = config
        # Data for the local folders, new format
       # self.get_local()
        self.init_local()
        if not os.path.isfile(getrealhome(self.config.statusfile_path)):
            log.error("No remote file found, creating " + getrealhome(self.config.statusfile_path))
            self.create_remote_statusfile()
       # else:
       #     self.get_remote()
        self.init_remote()
        self.init_statusfile()
        self.first_sync()


# TODO: use sync_folder instead of path everywhere, call them snyc_folders in config.yaml

#
    def refresh(self, key):
        self.update_local()
        self.update_remote()

#
    def get_local(self):
        for sync_folder in self.config.folders:
            self.register_local_folder(sync_folder)

#
    def get_remote(self):
        try:
            with open(getrealhome(self.config.statusfile_path), 'r') as stream:
                try:
                    self.remote = yaml.load(stream)
                except yaml.YAMLError as exc:
                    log.error(exc)
                    return("YAMLError")
        except FileNotFoundError:
            log.error("File " + getrealhome(self.config.statusfile_path) + " does not exist")
            return("FileNotFoundError")


    def init_local(self):
        self.local = {}
        #gets list of files in local
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            self.local[sync_folder_path] = {}
            for path, subdirs, files in os.walk(getrealhome(sync_folder_path)):
                for name in files:
                    obj = os.path.join(path, name)
                    self.set_local_record(sync_folder_path, getenvhome(obj), 'exists')

    def init_remote(self):
        self.remote = {}
        #gets list of files in remote
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            self.remote[sync_folder_path] = {}
            for path, subdirs, files in os.walk(getrealhome(self.config.enc_mainfolder)):
                for name in files:
                    obj = os.path.join(path, name)
                    self.set_remote_record(sync_folder_path, getenvhome(obj), 'exists')

    def init_statusfile(self):
        self.status = {}

    def first_sync(self):
        local_set = self.get_set(self.local)
        remote_set = self.get_set(self.remote)
        print("###############")
        print(remote_set)
        # if local but not remote, not status -> copy to remote, update status
        for obj in local_set - remote_set:
            print("NEW LOCAL OBJECT")
            print(obj)
            managed_file = File(obj)
            managed_file.encrypt(obj, self.config)
            self.set_status_record(obj, 'exists')
        # if remote but not local, not status -> copy to local, update status
        for obj in remote_set - local_set:
            print("NEW REMOTE OBJECT")
            print(obj)
            managed_file = File(obj)
            managed_file.decrypt(obj, self.config)
            #self.set_status_record(obj, 'exists')
        # if remote but not local, not status -> copy to local, update status
        # if local and status but not remote -> delete local, mark deleted on status
        # if remote and status but not local -> delete remote, mark deleted on status
        # if local and remote but not status -> check timestamp, choose newer, update status
        # if status but not local and not remote -> mark deleted on status
        pass

    def get_set(self, entries):
        object_set = set()
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            for obj in entries[sync_folder_path]:
                object_set.add(obj)
        return object_set


    def continuous_sync(self):
        print(self.local)
        print("----")
        print(self.remote)
        print("----")
        print(self.status)
        # if local but not remote, not status -> copy to remote, update status
        # if remote but not local, not status -> copy to local, update status
        # if local and status but not remote -> delete local, mark deleted on status
        # if remote and status but not local -> delete remote, mark deleted on status
        # if local and remote but not status -> check timestamp, choose newer, update status
        # if status but not local and not remote -> mark deleted on status
        pass

#
    def update_local(self):
        log.debug("######## Updating LOCAL")
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            log.debug("Updating folder " + sync_folder_path)
            objects = glob.glob(getrealhome(sync_folder_path) + "/**/*", recursive=True)

            registered_set = self.get_local_files_w_state(sync_folder_path, ('exists', 'recreated'))
            object_set = set()
            for obj in objects:
                if os.path.isfile(obj):
                    object_set.add(getenvhome(obj))
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
                local_file_timestamp = float(self.local[sync_folder_path][obj]['local_file_timestamp'])
                if tstamp(obj) > local_file_timestamp:
                    if not hash(obj) == self.local[sync_folder_path][obj]['local_file_checksum']:
                        log.debug(obj + " has changed contents locally")
                        self.set_local_file_record(sync_folder_path, obj, '')
                    else:
                        log.debug(obj + " has been updated locally but did not change")

            log.debug(" - Local files marked as EXISTING:")
            log.debug(self.get_local_files_w_state(sync_folder_path, ('exists')))
            log.debug(" - Local files marked as DELETED:")
            log.debug(self.get_local_files_w_state(sync_folder_path, ('deleted')))
            log.debug(" - Local files marked as RECREATED:")
            log.debug(self.get_local_files_w_state(sync_folder_path, ('recreated')))


    def update_remote(self):
        log.debug("######## Updating REMOTE")
        self.get_remote()
        # once remote is loaded, we compare, change(encrypt and update data), write statusfile again
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            log.debug("Updating remote folder " + sync_folder_path)
            registered_local_set = self.get_local_files_w_state(sync_folder_path, ('exists', 'recreated', 'deleted'))
            # TODO: get also the real remote files to compare
            registered_remote_set = self.get_remote_files_w_state(sync_folder_path, ('exists', 'recreated', 'deleted'))
            log.debug(" - Files in Local:")
            log.debug(registered_local_set)
            log.debug(" - Files in Remote:")
            log.debug(registered_remote_set)
            # is local but not remote? - NOT INCLUDING MARKED AS DELETED
            log.debug(" - Files not in Remote:")
            print(" - Files not in Remote:")
            for obj in registered_local_set - registered_remote_set:
                log.debug("   - " + obj)
                print("   - " + obj)
                managed_file = File(obj)
                enc_file_path = self.local[sync_folder_path][obj]['encrypted_file_path']
                managed_file.encrypt(enc_file_path, self.config)
                self.set_remote_file_record(sync_folder_path, obj, 'exists')
            log.debug(" - Files not in Local:")
            print(" - Files not in Local:")
            # is remote but not local? - NOT INCLUDING MARKED AS DELETED
            for obj in registered_remote_set - registered_local_set:
                log.debug("   - " + obj)
                print("   - " + obj)
                managed_file = File(obj)
                enc_file_path = self.remote[sync_folder_path][obj]['encrypted_file_path']
                managed_file.decrypt(enc_file_path, self.config)
                self.set_local_file_record(sync_folder_path, obj, 'exists')
            log.debug(" - Files in both:")
            print(" - Files in both:")
            # is on both? INCLUDING MARKED AS DELETED
            for obj in registered_local_set.intersection(registered_remote_set):
                log.debug("   - " + obj)
                print("   - " + obj)
                print("local:")
                print(float(self.local[sync_folder_path][obj]['remote_file_timestamp']))
                print("remote:")
                print(float(self.remote[sync_folder_path][obj]['remote_file_timestamp']))
                if float(self.local[sync_folder_path][obj]['local_file_timestamp']) > float(self.remote[sync_folder_path][obj]['remote_file_timestamp']):
                    self.update_remote_file(sync_folder_path, obj)
                elif float(self.local[sync_folder_path][obj]['local_file_timestamp']) < float(self.remote[sync_folder_path][obj]['remote_file_timestamp']):
                    # not there on first run
                    if self.local[sync_folder_path][obj]['remote_file_checksum'] != self.remote[sync_folder_path][obj]['remote_file_checksum']:
                        self.update_local_file(sync_folder_path, obj)
                else:
                    log.debug("     + both are the same")
        # TODO: when shall I write? 
        # TODO: do I need to reload? what if I remove files on the fly?
        self.write_remote_statusfile()


    def update_local_file(self, sync_folder_path, object):
        log.debug("     * remote is newer - " + self.remote[sync_folder_path][object]['state'])
        if self.remote[sync_folder_path][object]['state'] == 'deleted':
            log.debug("      -> removing " + object)
            os.remove(getrealhome(object))
        else:
            log.debug("      -> updating local " + object)
            managed_file = File(object)
            enc_file_path = self.remote[sync_folder_path][object]['encrypted_file_path']
            managed_file.decrypt(enc_file_path, self.config)
        self.set_local_file_record(sync_folder_path, object, self.remote[sync_folder_path][object]['state'])


    def update_remote_file(self, sync_folder_path, object):
        log.debug("     * local is newer - " + self.local[sync_folder_path][object]['state'])
        if self.local[sync_folder_path][object]['state'] == 'deleted':
            try:
                os.remove(enc_homefolder(self.config, self.local[sync_folder_path][object]['encrypted_file_path']))
                log.info("      -> removing  " + self.local[sync_folder_path][object]['encrypted_file_path'])
            except FileNotFoundError:
                pass
        else:
            log.info("      -> updating " + self.local[sync_folder_path][object]['encrypted_file_path'])
            managed_file = File(object)
            enc_file_path = self.remote[sync_folder_path][object]['encrypted_file_path']
            managed_file.encrypt(enc_file_path, self.config)
        self.set_remote_file_record(sync_folder_path, object, self.local[sync_folder_path][object]['state'])



    # Delete when set_local_record is working
    def set_local_file_record(self, sync_folder_path, local_file, state):
        if local_file not in self.local[sync_folder_path]:
            self.local[sync_folder_path][local_file] = {}
        # TODO: error if it does not exist maybe?
        real_local_file = getrealhome(local_file)
        for i in range(100000):
            dec_done = os.path.isfile(real_local_file)
            if dec_done:
                break
            else:
                continue
        self.local[sync_folder_path][local_file]['local_file_timestamp'] = tstamp(real_local_file)
        self.local[sync_folder_path][local_file]['local_file_checksum'] = hash(real_local_file)
        try:
            self.local[sync_folder_path][local_file]['remote_file_checksum'] = self.remote[sync_folder_path][local_file]['remote_file_checksum']
        except AttributeError: 
            self.local[sync_folder_path][local_file]['remote_file_checksum'] = ''
        self.local[sync_folder_path][local_file]['encrypted_file_path'] = self.config.enc_mainfolder + "/" + local_file.replace('$HOME', '_HOME') + ".gpg"
        if state == 'deleted':
            self.local[sync_folder_path][local_file]['local_file_timestamp'] = format(time.time())
        # Set no state to keep the same one
        if not state == '':
            self.local[sync_folder_path][local_file]['state'] = state

    # Improved version of set_local_file_record
    def set_local_record(self, sync_folder_path, local_file, state):
        if local_file not in self.local[sync_folder_path]:
            self.local[sync_folder_path][local_file] = {}
        self.local[sync_folder_path][local_file]['local_file_timestamp'] = tstamp(local_file)
        self.local[sync_folder_path][local_file]['local_file_checksum'] = hash(local_file)

        
    # Delete when set_remote_record is working
    def set_remote_file_record(self, sync_folder_path, remote_file, state):
        if remote_file not in self.remote[sync_folder_path]:
            self.remote[sync_folder_path][remote_file] = {}
        # TODO: error if it does not exist maybe?
        real_remote_file = enc_homefolder(self.config, self.local[sync_folder_path][remote_file]['encrypted_file_path'])
        for i in range(1000):
            enc_done = os.path.isfile(real_remote_file)
            if enc_done:
                break
            else:
                continue
        self.remote[sync_folder_path][remote_file]['remote_file_timestamp'] = tstamp(real_remote_file)
        self.remote[sync_folder_path][remote_file]['remote_file_checksum'] = hash(real_remote_file)
        self.local[sync_folder_path][remote_file]['remote_file_timestamp'] = tstamp(real_remote_file)
        self.local[sync_folder_path][remote_file]['remote_file_checksum'] = hash(real_remote_file)
        self.remote[sync_folder_path][remote_file]['encrypted_file_path'] = self.local[sync_folder_path][remote_file]['encrypted_file_path']
        # Set no state to keep the same one
        if not state == '':
            self.remote[sync_folder_path][remote_file]['state'] = state


    # Improved version of set_remote_file_record
    def set_remote_record(self, sync_folder_path, remote_file, state):
        file_path = dec_path(remote_file, self.config)
        if file_path not in self.remote[sync_folder_path]:
            self.remote[sync_folder_path][file_path] = {}
        self.remote[sync_folder_path][file_path]['remote_file_timestamp'] = tstamp(remote_file)
        self.remote[sync_folder_path][file_path]['remote_file_checksum'] = hash(remote_file)
        
    def set_status_record(self, status_file, state):
        if status_file not in self.status:
            self.status[status_file] = {}
        self.status[status_file]['local_file_checksum'] = hash(status_file)
        self.status[status_file]['remote_file_checksum'] = hash(status_file)

    def create_remote_statusfile(self):
        self.remote = {}
        for sync_folder in self.config.folders:
            self.remote[sync_folder['path']] = {}
        self.write_remote_statusfile()


    def write_remote_statusfile(self):
        log.debug("######## Writing to status file: " + getrealhome(self.config.statusfile_path))
        with open(getrealhome(self.config.statusfile_path), 'w') as outfile:
            yaml.dump(self.remote, outfile, default_flow_style=False)


    def get_local_files(self, sync_folder_path):
        result = set()
        for file in self.local[sync_folder_path]:
            result.add(file)
        return result


    def get_local_files_w_state(self, sync_folder_path, state):
        result = set()
        for file in self.local[sync_folder_path]:
            if self.local[sync_folder_path][file]['state'] in state:
                result.add(file)
        return result


    def get_remote_files_w_state(self, sync_folder_path, state):
        result = set()
        for file in self.remote[sync_folder_path]:
            if self.remote[sync_folder_path][file]['state'] in state:
                result.add(file)
        return result


    def register_local_folder(self, sync_folder):
        sync_folder_path = sync_folder['path']
        self.local[sync_folder_path] = {}
        objects = glob.glob(getrealhome(sync_folder_path) + "/**/*", recursive=True) 
        for obj in objects:
            if os.path.isfile(obj):
                self.set_local_file_record(sync_folder_path, getenvhome(obj), 'exists')

        
    def new_local_file(self, sync_folder_path, local_file): 
        self.set_local_file_record(sync_folder_path, local_file, 'exists')

        
    def delete_local_file(self, sync_folder_path, local_file): 
        self.set_local_file_record(sync_folder_path, local_file, 'deleted')
        
        
    def recreate_local_file(self, sync_folder_path, local_file): 
        self.set_local_file_record(sync_folder_path, local_file, 'recreated')
        
