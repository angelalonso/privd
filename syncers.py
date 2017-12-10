import glob
import logging as log
import os
import subprocess
import sys
import time

from files import File as File
from tools import get_hash as hash
from tools import get_newer as newer
from tools import get_timestamp as tstamp
from status import Status


class Syncer(object):
    """ A syncer object which contains:
    folders to be encrypted
    details about the encryption
    details to identify newer versions -> Moved to Files maybe?
    """

    def __init__(self, config, key):
        """ Checks that everything is coherent between local and remote(encrypted) copies
        """
        self.config = config
        self.key = key

        self.status = Status(self.config)

        if not os.path.exists(self.config.enc_mainfolder):
            os.makedirs(self.config.enc_mainfolder)

        for folder in self.config.dec_folders:
            self.folder_initialize(folder['path'])

        if not os.path.isfile(self.config.statusfile_path):
            self.status.write_statusfile()


    def refresh(self):
        for folder in self.config.dec_folders:
            self.folder_initialize(folder['path'])
 
        objects = glob.glob(folder['path'] + "/**/*", recursive=True)
        for obj in objects:
            if os.path.isfile(obj):
                self.status.add_file(folder['path'], obj)
            elif os.path.isdir(obj):
                if not os.path.exists(obj):
                    os.makedirs(obj)


    def auto(self):

        self.status.load_statusfile()

        files, not_in_dec, not_in_enc, in_both = self.status.compare()
        log.debug("FILES NOT IN DEC")
        log.debug(not_in_dec)
        log.debug("FILES NOT IN ENC")
        log.debug(not_in_enc)
        log.debug("FILES IN BOTH")
        log.debug(in_both)

        # TODO: check details again?

        # Case #1: Files in remote are not in local
        for file in not_in_dec:
            managed_file = File(file)
            # TODO: overwrite dec_folders' encrypted_path with the one from enc_folders
            log.debug("decrypting " + file + " from " + self.status.enc_folders[self.status.get_folder(file,self.status.enc_folders)][file]['encrypted_path'])
            managed_file.decrypt(self.status.enc_folders[self.status.get_folder(file,self.status.enc_folders)][file]['encrypted_path'])

        # Case #2: Files in local are not in remote
        for file in not_in_enc:
            print("#----------------------------------#" + file)
            print(str(self.status.dec_folders))
            print("#----------------------------------#")
            managed_file = File(file)
            path = self.status.get_folder(file,self.status.dec_folders)
            enc_file_path = file.replace(path, self.config.enc_mainfolder + path) + '.gpg'
            managed_file.encrypt(enc_file_path, self.key)
            # This is needed because the encryption takes a bit. 100 is a random number really

            print("##++++++++### " + str(self.status.dec_folders[path][file]))
            for i in range(1000):
                try:
                    self.status.add_file(path, file)
                    #self.status.add_encrypted_file(path, file, self.status.dec_folders[file]['encrypted_path'])
                except FileNotFoundError:
                    continue
                break
            print("##++++++++### " + str(self.status.dec_folders[path][file]))
        print("####################################")
        print(str(self.status.dec_folders))

        # Case #3: Files in both
        for file in in_both:
            folder = self.status.get_folder(file,self.status.enc_folders)
            dec_details = self.status.dec_folders[folder][file]
            enc_details = self.status.enc_folders[folder][file]
            #a) modification for both
            if dec_details['file_checksum'] != enc_details['file_checksum']:
                if dec_details['file_timestamp'] >= enc_details['file_timestamp']:
                    managed_file = File(file)                                                                                                                
                    path = self.status.get_folder(file,self.status.dec_folders)                                                                              
                    enc_file_path = file.replace(path, self.config.enc_mainfolder + path) + '.gpg'                                                           
                    managed_file.encrypt(enc_file_path, self.key)                                                                                            
                    # This is needed because the encryption takes a bit. 100 is a random number really                                                       
                    for i in range(1000):                                                                                                                    
                        try:                                                                                                                                 
                            self.status.add_encrypted_file(path, file, enc_file_path)                                                                        
                        except FileNotFoundError:                                                                                                            
                            continue                                                                                                                         
                        break        
                else:
                    managed_file = File(file)
                    # TODO: overwrite dec_folders' encrypted_path with the one from enc_folders
                    log.debug("decrypting " + file + " from " + self.status.enc_folders[self.status.get_folder(file,self.status.enc_folders)][file]['encrypted_path'])
                    managed_file.decrypt(self.status.enc_folders[self.status.get_folder(file,self.status.enc_folders)][file]['encrypted_path'])



        self.status.write_statusfile()
        self.status.load_statusfile()
        #print("############# " + str(self.status.dec_folders['/home/aaf/.privd/TEST/source']['/home/aaf/.privd/TEST/source/beep']))
        #print("############# " + str(self.status.enc_folders['/home/aaf/.privd/TEST/source']['/home/aaf/.privd/TEST/source/beep']))
            

    def folder_initialize(self, path):
        if not os.path.exists(path):
            log.debug("Creating folder " + path)
            os.makedirs(path)
        elif os.path.isfile(path):
            log.debug("Error! Folder name " + path + " already exists and it's a file")
        self.status.add_folder(path)
        objects = glob.glob(path + "/**/*", recursive=True)
        for obj in objects:
            if os.path.isfile(obj):
                self.status.add_file(path, obj)


    def folder_encrypt(self, path, enc_mainfolder, key):
        objects = glob.glob(path + "/**/*", recursive=True)

        # Create the folder as such within the enc folder
        enc_path = path.replace(path, enc_mainfolder + path)
        if not os.path.exists(enc_path):
            log.debug("Creating folder " + enc_path)
            os.makedirs(enc_path)

        for obj in objects:
            self.status.add_file(path, obj)
            enc_obj_path = obj.replace(path, enc_mainfolder + path) + '.gpg'
            if os.path.isfile(obj):
                managed_file = File(obj)
                managed_file.encrypt(enc_obj_path, key)
                # This is needed because the encryption takes a bit. 100 is a random number really
                for i in range(1000):
                    try:
                        self.status.add_encrypted_file(path, obj, enc_obj_path)
                    except FileNotFoundError:
                        continue
                    break
            elif os.path.isdir(obj):
                if not os.path.exists(enc_obj_path):
                    os.makedirs(enc_obj_path)
        self.status.write_statusfile()
        self.status.load_statusfile()


    def folder_decrypt(self, path, enc_mainfolder, key):
        objects = glob.glob(enc_mainfolder + path + "/**/*", recursive=True)
        log.debug(path)
        log.debug(enc_mainfolder)

        # Create the folder to decrypt file to if it isn't there already
        if not os.path.exists(path):
            log.debug("Creating folder " + path)
            os.makedirs(path)
        for obj in objects:
            log.debug(obj)
            dec_obj_path = obj.replace(enc_mainfolder + path, path).replace('.gpg','')
            log.debug(dec_obj_path)
            if os.path.isfile(obj):
                managed_file = File(dec_obj_path)
                managed_file.decrypt(obj)
            elif os.path.isdir(obj):
                if not os.path.exists(dec_obj_path):
                    os.makedirs(dec_obj_path)
      
