import glob
import logging as log
import os
import pprint
import time
import yaml
from files import File as File
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome
from tools import enc_homefolder
from tools import get_encrypted_file_path as enc_path
from tools import get_decrypted_file_path as dec_path
from tools import get_sync_folder_path
from tools import checksum as hash
from tools import timestamp as tstamp

class Status(object):
    def __init__(self, config):
        # Config coming from the syncer
        self.config = config
        self.read_local()
        self.read_remote()
        self.read_statusfile()
        self.first_sync()


    def read_local(self):
        self.local = {}
        #gets list of files in local
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            self.local[sync_folder_path] = {}
            for path, subdirs, files in os.walk(getrealhome(sync_folder_path)):
                for name in files:
                    obj = os.path.join(path, name)
                    self.set_local_record(sync_folder_path, getenvhome(obj), 'exists')


    def read_remote(self):
        self.remote = {}
        #gets list of files in remote
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            self.remote[sync_folder_path] = {}
            for path, subdirs, files in os.walk(getrealhome(self.config.enc_mainfolder)):
                for name in files:
                    obj = os.path.join(path, name)
                    self.set_remote_record(sync_folder_path, getenvhome(obj), 'exists')


    def read_statusfile(self):
        try:
            with open(getrealhome(self.config.statusfile_path), 'r') as stream:
                try:
                    self.status = yaml.load(stream)
                except yaml.YAMLError as exc:
                    log.error(exc)
                    return("YAMLError")
        except FileNotFoundError:
            log.error("File " + getrealhome(self.config.statusfile_path) + " does not exist")
            log.error("No remote file found, creating " + getrealhome(self.config.statusfile_path))
            self.create_statusfile()


    def create_statusfile(self):
        self.status = {}
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            self.status[sync_folder_path] = {}
        self.write_statusfile()


    def write_statusfile(self):
        log.debug("######## Writing to status file: " + getrealhome(self.config.statusfile_path))
        with open(getrealhome(self.config.statusfile_path), 'w') as outfile:
            yaml.dump(self.status, outfile, default_flow_style=False)

    def syncer(self):
        '''
        - status keeps tstamp and hash of local and remote
          - must be kept updated at all times
        PHASE
        +a+status+b - everywhere 
          - status deleted? -> delete it on a and b
          - 

        +a+status-b - deleted on b
          - status deleted? -> delete it on a
          - a newer than status_b and status_a? -> update status_a, recreate on b
          - a newer than status_b? -> recreate on b
          - a newer than status_a? -> update status_a, mark as deleted, delete from a
          - status_a newer than a? -> mark as deleted, delete from a
        +a-status+b - status is missing 
          -> same as +a+status+b
        +a-status-b - created on a
         -> add it to b and status
        -a+status+b - deleted on a
          - status deleted? -> delete it on b
          - b newer than status_a and status_b? -> update status_b, recreate on a
          - b newer than status_a? -> recreate on a
          - b newer than status_b? -> update status_b, mark as deleted, delete from b
          - status_b newer than b? -> mark as deleted, delete from b
        -a+status-b - files does not actually exist, status is wrong
         -> mark status as deleted
        -a-status+b - created on b
         -> add it to a and status
        -a-status-b - it does not exist, nothing to do
         - nothing to compare


        
        '''
        pass

    def first_sync(self):
        pp = pprint.PrettyPrinter(indent=4)
        print("-- local --")
        pp.pprint(self.local)
        print("-- remote --")
        pp.pprint(self.remote)
        print("-- status --")
        pp.pprint(self.status)
        local_set = self.get_set(self.local)
        remote_set = self.get_set(self.remote)
        status_set = self.get_set(self.status)
        # if local but not remote, not status -> copy to remote, update status
        for obj in local_set - remote_set - status_set:
            print("NEW LOCAL OBJECT")
            print(obj)
            managed_file = File(obj)
            managed_file.encrypt(obj, self.config)
            self.set_remote_record(get_sync_folder_path(obj, self.config), getenvhome(obj), 'exists')
            self.set_status_record(obj, 'exists')
        # if remote but not local, not status -> copy to local, update status
        for obj in remote_set - local_set - status_set:
            print("NEW REMOTE OBJECT")
            print(obj)
            managed_file = File(obj)
            managed_file.decrypt(obj, self.config)
            self.set_local_record(get_sync_folder_path(obj, self.config), getenvhome(obj), 'exists') 
            self.set_status_record(obj, 'exists')
        # if local and status but not remote -> delete local, mark deleted on status
        for obj in local_set - remote_set:
            if obj in status_set:
                print("DELETED REMOTE OBJECT")
                print(obj)
                try: #it could have been deleted meanwhile
                    os.remove(obj)
                except FileNotFoundError: pass
                self.set_status_record(obj, 'deleted')
        # if remote and status but not local -> delete remote, mark deleted on status
        for obj in remote_set - local_set:
            if obj in status_set:
                print("DELETED LOCAL OBJECT")
                print(obj)
                os.remove(getrealhome(enc_path(obj, self.config)))
                self.set_status_record(obj, 'deleted')
        # if local and remote but not status -> check timestamp, choose newer, update status
        for obj in local_set.intersection(status_set):
            if obj not in status_set:
                print("OBJECT IN BOTH, NO STATUS")
            else:
                print("OBJECT IN LOCAL, REMOTE AND STATUS")
        # if status but not local and not remote -> mark deleted on status
        for obj in status_set - local_set:
            if obj not in remote_set:
                print("OBJECT IN STATUS AND STATUS ONLY")
                self.set_status_record(obj, 'deleted')
        # OTHER:
        # if remote checksum in status and remote are different but timestamps are equal: recheck checksum
        self.write_statusfile()
        self.read_statusfile()


    def resolve_conflict(self, obj):
        # Check if we have status of that object
        real_remote_file = enc_homefolder(self.config, enc_path(obj, self.config))
        try:
            current_status = self.status[get_sync_folder_path(obj, self.config)][obj]
            #Remote has changed
            if current_status['remote_file_checksum'] != hash(real_remote_file):
                if current_status['remote_file_timestamp'] < tstamp(real_remote_file):
                    print("NEWER REMOTE OBJECT")
                    print(obj)
                    managed_file = File(obj)                       
                    managed_file.decrypt(obj, self.config)         
                    self.set_local_record(get_sync_folder_path(obj, self.config), getenvhome(obj), 'exists') 
                    self.set_status_record(obj, 'exists') 
                elif current_status['remote_file_timestamp'] > tstamp(real_remote_file):
                    print("ERROR: status has a newer remote timestamp")
            #Local has changed
            if current_status['local_file_checksum'] != hash(obj):
                if current_status['local_file_timestamp'] < tstamp(obj):
                    print("NEWER LOCAL OBJECT")
                    print(obj)
                    managed_file = File(obj)                       
                    managed_file.encrypt(obj, self.config)         
                    self.set_remote_record(get_sync_folder_path(obj, self.config), getenvhome(obj), 'exists')
                    self.set_status_record(obj, 'exists') 
        
                #update 
            #Both have changed
            print("++++")
            print(current_status)
            print("----")
        except KeyError:
            print("////")

        # WHat happens if timestamp or remote is newer, then we update, then the other one and so on?

    def get_set(self, entries):
        object_set = set()
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            for obj in entries[sync_folder_path]:
                object_set.add(obj)
        return object_set


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
            self.set_local_record(get_sync_folder_path(object, self.config), getenvhome(object), 'exists') 
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
            self.set_remote_record(get_sync_folder_path(object, self.config), getenvhome(object), 'exists')
        self.set_remote_file_record(sync_folder_path, object, self.local[sync_folder_path][object]['state'])



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
        #NEEDED?
        #for i in range(1000):
        #    enc_done = os.path.isfile(real_remote_file)
        #    if enc_done:
        #        break
        #    else:
        #        continue
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
        

    def set_status_record(self, local_file, state):
        sync_folder_path = get_sync_folder_path(local_file, self.config)
        if local_file not in self.status[sync_folder_path]:
            self.status[sync_folder_path][local_file] = {}
        real_remote_file = enc_homefolder(self.config, enc_path(local_file, self.config))
        if state != 'deleted':
            self.status[sync_folder_path][local_file]['local_file_checksum'] = hash(local_file)
            self.status[sync_folder_path][local_file]['local_file_timestamp'] = tstamp(local_file)
            self.status[sync_folder_path][local_file]['remote_file_checksum'] = hash(real_remote_file)
            self.status[sync_folder_path][local_file]['remote_file_timestamp'] = tstamp(real_remote_file)
            self.status[sync_folder_path][local_file]['remote_file_path'] = real_remote_file
        self.status[sync_folder_path][local_file]['state'] = state


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

#
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

