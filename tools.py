#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-
                             
                              
import datetime
import hashlib
import math
import os


from gui import MyGUI as Gui


def real2homeenv_path(path):
    """ replaces /home/user OR /Users/user with $HOME
    """
    # TODO: identify other environment vars (from $ to ...)
    new_path = path.replace(os.environ['HOME'], '$HOME')
    return new_path


def homeenv2real_path(path):
    """ replaces $HOME with /home/user OR /Users/user 
    """
    # TODO: identify other environment vars (from $ to ...)
    new_path = path.replace('$HOME', os.environ['HOME'])
    return new_path

def enc_homefolder(config, path):
    """ returns path parameter with the real HOME folder path 
    """
    real_enc_mainfolder =  config.enc_mainfolder.replace('$HOME', os.environ['HOME'])
    new_path = path.replace(config.enc_mainfolder, real_enc_mainfolder)
    return new_path

def get_filesize(file):
    """ returns the filesize of a given file as String
    """
    path = homeenv2real_path(file)
    size_bytes = os.stat(homeenv2real_path(path)).st_size
   #https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python 
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def get_encrypted_file_path(file, config):
    """ returns the path to the encrypted copy of the file
    """
    filepath = file.replace('$HOME', '/_HOME')
    return config.enc_mainfolder + filepath + '.gpg'

def get_decrypted_file_path(enc_file, config):
    """ returns the path to the decrypted copy of the file
    """
    result = enc_file.replace('.gpg','').replace(config.enc_mainfolder + '/', '').replace('_HOME', '$HOME')
    return result


def get_sync_folder_path(file, config):
    """ returns the folder our file is on,
        from the configured folders we have
    """
    result = 'path'
    for folder in config.folders:
        if folder['path'] + '/' in file:
            result = folder['path']
            break
    return result


def timestamp(file):
    """ gets the timestamp of a given file
    """
    realfile = homeenv2real_path(file)
    if os.path.isfile(realfile):
        return format(os.stat(realfile).st_mtime)
    else:
        return 0


def beauty_timestamp(timestamp):
    """ returns a readable version of a timestamp
    """
    beauty = datetime.datetime.fromtimestamp(
            float(timestamp)).strftime('%d-%m-%Y %H:%M:%S')
    return beauty


def checksum(file_in):
    """ Gets the checksum of the file                                                                                                                           
    Hashlib part taken from https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    """                       
    # We'll read in 64kb chunks
    BUF_SIZE = 65536          
    # SHA1 one is enough for this
    sha1 = hashlib.sha1()     
    realfile = homeenv2real_path(file_in)
    #First, wait for the file to be there
    for i in range(10000):                                  
        file_created = os.path.isfile(realfile)        
        if file_created:                                       
            break                                          
        else:                                              
            continue
    #TODO: check that the file is indeed not meant to be an empty one
    #second, wait for it to have content
    for i in range(1000000):                                  
        enc_done = os.stat(realfile).st_size        
        if enc_done > 0:                                       
            break                                          
        else:                                              
            continue
        gui.info("file " + realfile + " is an empty one, is it needed?")
    try:                      
        with open(realfile, 'rb') as f:
            while True:       
                data = f.read(BUF_SIZE)
                if not data:  
                    break     
                sha1.update(data)
        file_sha1 = "{0}".format(sha1.hexdigest())
    except FileNotFoundError: 
        gui.debug("File " + file_in + " does not exist")
        file_sha1 = ''
    except IsADirectoryError:
        gui.debug("File " + file_in + " is a directory")
        file_sha1 = ''
    return file_sha1
