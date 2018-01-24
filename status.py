#!/usr/bin/python3

# -*- coding: utf-8 -*-

#  ====  Automated Import and pip-installation of requirements  ====  #
import subprocess             
                              
def pipinstall(package):      
    subprocess.call(['pip3', 'install', '--user', package])                                                                                                                                           
                 

try: import glob
except ImportError:           
    pipinstall('glob')     
    import glob
                   
try: import logging as log    
except ImportError:           
    pipinstall('logging')     
    import logging as log     
                   
try: import os                
except ImportError:           
    pipinstall('os')          
    import os                 
              
try: import yaml
except ImportError:           
    pipinstall('pyyaml')     
    import yaml


from files import File as File
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome
from tools import enc_homefolder
from tools import get_encrypted_file_path as enc_path
from tools import get_decrypted_file_path as dec_path
from tools import get_sync_folder_path
from tools import checksum
from tools import timestamp as tstamp


class Status(object):
    """ An object to control and manage files that will be synced
    """
    def __init__(self, config, key):
        self.config = config
        self.config.key = key

        if not os.path.exists(getrealhome(self.config.enc_mainfolder)):
            log.debug("Encrypted Main Folder does not exist, creating " + getrealhome(self.config.enc_mainfolder))
            os.makedirs(getrealhome(self.config.enc_mainfolder))
        
        log.debug("pre local")
        self.read_local()
        log.debug("local done")
        self.read_remote()
        self.read_statusfile()


    def check_n_sync(self):
        self.read_local()
        self.read_remote()
        self.executer()


    def read_local(self):
        self.local = {}
        files = []
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            self.local[sync_folder_path] = {}
            for path, subdirs, files in os.walk(getrealhome(sync_folder_path)):
                for name in files:
                    obj = os.path.join(path, name)
                    self.set_local_record(sync_folder_path, getenvhome(obj), 'exists')
        return len(files)


    def read_remote(self):
        self.remote = {}
        files = []
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            self.remote[sync_folder_path] = {}
            for path, subdirs, files in os.walk(getrealhome(self.config.enc_mainfolder)):
                for name in files:
                    obj = os.path.join(path, name)
                    self.set_remote_record(sync_folder_path, getenvhome(obj), 'exists')
        return len(files)


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
        log.debug("- Writing to status file: " + getrealhome(self.config.statusfile_path))
        with open(getrealhome(self.config.statusfile_path), 'w') as outfile:
            yaml.dump(self.status, outfile, default_flow_style=False)


    def executer(self):
        local_set = self.get_set(self.local)
        remote_set = self.get_set(self.remote)
        status_set = self.get_set(self.status)

        everywhere = local_set.intersection(remote_set).intersection(status_set)
        log.debug("  +local+status+remote - files managed everywhere")
        for obj in everywhere:
            log.debug(obj)
            self.resolve_conflict(obj)
        
        deleted_on_b = local_set.intersection(status_set) - remote_set
        log.debug("  +local+status-remote - deleted on remote")
        for obj in deleted_on_b:
            log.debug(obj)
            self.deleted_remote_file(obj)
        
        missing_status = local_set.intersection(remote_set) - status_set
        log.debug("  +local-status+remote - status is missing")
        for obj in missing_status:
            log.debug(obj)
            self.resolve_conflict_no_status(obj)
        
        created_on_a = local_set - status_set - remote_set
        log.debug("  +local-status-remote - created on local")
        for obj in created_on_a:
            log.debug(obj)
            self.created_local_file(obj)
        
        deleted_on_a = remote_set.intersection(status_set) - local_set
        log.debug("  -local+status+remote - deleted on local")
        for obj in deleted_on_a:
            log.debug(obj)
            self.deleted_local_file(obj)
        
        status_wrong = status_set - local_set - remote_set
        log.debug("  -local+status-remote - file does not actually exist, status is wrong")
        for obj in status_wrong:
            log.debug(obj)
            del self.status[get_sync_folder_path(object, self.config)][obj]
        
        created_on_b = remote_set - status_set - local_set
        log.debug("  -local-status+remote - created on remote")
        for obj in created_on_b:
            log.debug(obj)
            self.created_remote_file(obj)

        # ...and -a-status-b, which means nothing to do
        self.write_statusfile()
        self.read_statusfile()

# ----------------------------- Conflict resolvers

    def resolve_conflict(self, obj):
        current_local = self.local[get_sync_folder_path(obj, self.config)][obj]
        current_remote = self.remote[get_sync_folder_path(obj, self.config)][obj]
        current_status = self.status[get_sync_folder_path(obj, self.config)][obj]
        
        local_age = current_local['local_file_timestamp']
        status_local_age = current_status['local_file_timestamp']
        status_remote_age = current_status['remote_file_timestamp']
        remote_age = current_remote['remote_file_timestamp']
        if local_age > status_local_age:
            if local_age > remote_age and not status_local_age == status_remote_age:
                log.debug("Conflict:" + obj + " local version changed")
                managed_file = File(obj, self.config.gui)
                managed_file.encrypt(obj, self.config)
                self.update_remote_record(obj)
                self.update_status_after_sync(obj, 'exists')
            else:
                log.debug("Conflict:" + obj + " local version is newer but no update is needed")
                self.update_status_from_local(obj)
        elif remote_age > status_remote_age:
            if remote_age > local_age and not status_remote_age == status_local_age:
                log.debug("Conflict:" + obj + " remote version changed")
                managed_file = File(obj, self.config.gui)
                managed_file.decrypt(obj, self.config)
                self.update_local_record(obj)
                self.update_status(obj, 'exists')
            else:
                log.debug("Conflict:" + obj + " remote version is newer but no update is needed")
                self.update_status_from_remote(obj)
        else:
            self.update_status(obj)


    def resolve_conflict_no_status(self, obj):
        current_local = self.local[get_sync_folder_path(obj, self.config)][obj]
        current_remote = self.remote[get_sync_folder_path(obj, self.config)][obj]
        
        local_age = current_local['local_file_timestamp']
        remote_age = current_remote['remote_file_timestamp']
        if local_age > remote_age:
            log.debug("Conflict:" + obj + " local version changed")
            managed_file = File(obj, self.config.gui)
            managed_file.encrypt(obj, self.config)
            self.update_remote_record(obj)
        elif remote_age > local_age:
            log.debug("Conflict:" + obj + " remote version changed")
            managed_file = File(obj, self.config.gui)
            managed_file.decrypt(obj, self.config)
            self.update_status(obj, 'exists')
        self.create_status_record(obj)
        self.update_status_after_sync(obj, 'exists')

#----------------------------- Recorded details Creators

    def create_status_record(self, object):
        sync_folder_path = get_sync_folder_path(object, self.config)
        real_remote_file = enc_homefolder(self.config, enc_path(object, self.config))
        self.status[sync_folder_path][object] = {}
        self.status[sync_folder_path][object]['local_file_checksum'] = self.local[sync_folder_path][object]['local_file_checksum']
        self.status[sync_folder_path][object]['local_file_timestamp'] = self.local[sync_folder_path][object]['local_file_timestamp']
        self.status[sync_folder_path][object]['remote_file_checksum'] = self.remote[sync_folder_path][object]['remote_file_checksum']
        self.status[sync_folder_path][object]['remote_file_timestamp'] = self.remote[sync_folder_path][object]['remote_file_timestamp']
        self.status[sync_folder_path][object]['remote_file_path'] = real_remote_file
        self.status[sync_folder_path][object]['state'] = 'exists'

#----------------------------- Recorded details Setters

    def set_local_record(self, sync_folder_path, local_file, state):
        if local_file not in self.local[sync_folder_path]:
            self.local[sync_folder_path][local_file] = {}
        real_remote_file = getrealhome(enc_path(local_file, self.config))

        self.local[sync_folder_path][local_file]['local_file_timestamp'] = tstamp(local_file)
        self.local[sync_folder_path][local_file]['local_file_checksum'] = checksum(local_file)
        try:
            self.local[sync_folder_path][local_file]['remote_file_checksum'] = checksum(real_remote_file)
        except FileNotFoundError:
            self.local[sync_folder_path][local_file]['remote_file_checksum'] = '0000'

        
    def set_remote_record(self, sync_folder_path, remote_file, state):
        local_file = dec_path(remote_file, self.config)
        if local_file not in self.remote[sync_folder_path]:
            self.remote[sync_folder_path][local_file] = {}
        self.remote[sync_folder_path][local_file]['remote_file_timestamp'] = tstamp(remote_file)
        checksum_remote_file = checksum(remote_file)
        self.remote[sync_folder_path][local_file]['remote_file_checksum'] = checksum_remote_file
        try:
            self.local[sync_folder_path][local_file]['remote_file_checksum'] = checksum_remote_file
        except KeyError:
            pass
        
#----------------------------- Recorded details Updaters

    def update_status(self, object, *args):
        sync_folder_path = get_sync_folder_path(object, self.config)
        if object not in self.status[sync_folder_path]:
            self.status[sync_folder_path][object] = {}
        state = ''
        for value in args:
            state += value
        if state != '':
            self.status[sync_folder_path][object]['state'] = state
        if state != 'deleted':
            self.status[sync_folder_path][object]['remote_file_timestamp'] = self.remote[sync_folder_path][object]['remote_file_timestamp']
            self.status[sync_folder_path][object]['remote_file_checksum'] = self.remote[sync_folder_path][object]['remote_file_checksum']
            self.status[sync_folder_path][object]['local_file_timestamp'] = self.local[sync_folder_path][object]['local_file_timestamp']
            self.status[sync_folder_path][object]['local_file_checksum'] = self.local[sync_folder_path][object]['local_file_checksum']
        else:
            del self.status[sync_folder_path][object]

        
    def update_status_after_sync(self, object, *args):
        # This is different from update_status in that,
        #   to avoid misunderstandings later, 
        #   we artificially set timestamps equal to local and remote
        sync_folder_path = get_sync_folder_path(object, self.config)
        if object not in self.status[sync_folder_path]:
            self.status[sync_folder_path][object] = {}
        state = ''
        for value in args:
            state += value
        if state != '':
            self.status[sync_folder_path][object]['state'] = state
        if state != 'deleted':
            remote_timestamp = self.remote[sync_folder_path][object]['remote_file_timestamp']
            local_timestamp = self.local[sync_folder_path][object]['local_file_timestamp']
            if remote_timestamp > local_timestamp: newest = remote_timestamp
            else: newest = local_timestamp
            self.status[sync_folder_path][object]['remote_file_timestamp'] = newest
            self.status[sync_folder_path][object]['remote_file_checksum'] = self.remote[sync_folder_path][object]['remote_file_checksum']
            self.status[sync_folder_path][object]['local_file_timestamp'] = newest
            self.status[sync_folder_path][object]['local_file_checksum'] = self.local[sync_folder_path][object]['local_file_checksum']
        else:
            del self.status[sync_folder_path][object]


    def update_status_from_remote(self, object):
        sync_folder_path = get_sync_folder_path(object, self.config)
        self.status[sync_folder_path][object]['remote_file_timestamp'] = self.remote[sync_folder_path][object]['remote_file_timestamp']
        self.status[sync_folder_path][object]['remote_file_checksum'] = self.remote[sync_folder_path][object]['remote_file_checksum']

    def update_status_from_local(self, object):
        sync_folder_path = get_sync_folder_path(object, self.config)
        self.status[sync_folder_path][object]['local_file_timestamp'] = self.local[sync_folder_path][object]['local_file_timestamp']
        self.status[sync_folder_path][object]['local_file_checksum'] = self.local[sync_folder_path][object]['local_file_checksum']

        
    def update_remote_record(self, object):
        sync_folder_path = get_sync_folder_path(object, self.config)
        real_remote_file = enc_homefolder(self.config, enc_path(object, self.config))
        if object not in self.remote[sync_folder_path]:
            self.remote[sync_folder_path][object] = {}
        self.remote[sync_folder_path][object]['remote_file_timestamp'] = tstamp(real_remote_file)
        self.remote[sync_folder_path][object]['remote_file_checksum'] = checksum(real_remote_file)
        self.local[sync_folder_path][object]['remote_file_checksum'] = self.remote[sync_folder_path][object]['remote_file_timestamp']

        
    def update_local_record(self, object):
        sync_folder_path = get_sync_folder_path(object, self.config)
        if object not in self.local[sync_folder_path]:
            self.local[sync_folder_path][object] = {}
        self.local[sync_folder_path][object]['local_file_timestamp'] = tstamp(object)
        self.local[sync_folder_path][object]['local_file_checksum'] = checksum(object)

#----------------------------- Creation handlers
        
    def created_local_file(self, obj):
        managed_file = File(obj, self.config.gui)
        managed_file.encrypt(obj, self.config)
        self.update_remote_record(obj)
        self.update_status_after_sync(obj, 'exists')


    def created_remote_file(self, obj):
        managed_file = File(obj, self.config.gui)
        managed_file.decrypt(obj, self.config)
        self.update_local_record(obj)
        self.update_status_after_sync(obj, 'exists')

#----------------------------- Deletion handlers

    def deleted_remote_file(self, obj):
        self.config.gui.info("removing " + getrealhome(obj))
        os.remove(getrealhome(obj))
        self.update_status(obj, 'deleted')
            
        
    def deleted_local_file(self, obj):
        real_remote_file = enc_homefolder(self.config, enc_path(obj, self.config))
        self.config.gui.info("removing " + real_remote_file)
        os.remove(real_remote_file)
        self.update_status(obj, 'deleted')

#----------------------------- Other functions

    def get_set(self, entries):
        object_set = set()
        for sync_folder in self.config.folders:
            sync_folder_path = sync_folder['path']
            for obj in entries[sync_folder_path]:
                object_set.add(obj)
        return object_set


    def old_sync_from_remote(self):
        for obj in glob.iglob(getrealhome(self.config.enc_mainfolder) + '/*', recursive=True):
                print("########")
                print(obj)
                print("########")
                if os.path.isfile(obj):
                    managed_file = File(obj, self.config.gui)
                    managed_file.decrypt(obj, self.config)
               

    def sync_from_remote(self):
        for path, subdirs, files in os.walk(getrealhome(self.config.enc_mainfolder)):
            print(files)
            for name in files:
                obj = dec_path(getenvhome(os.path.join(path, name)), self.config)
                managed_file = File(obj, self.config.gui)
                managed_file.decrypt(obj, self.config)


