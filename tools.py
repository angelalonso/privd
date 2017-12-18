import hashlib
import os
import logging as log


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
    real_enc_mainfolder =  config.enc_mainfolder.replace('$HOME', os.environ['HOME'])
    new_path = path.replace(config.enc_mainfolder, real_enc_mainfolder)
    return new_path

def get_encrypted_file_path(file, config, path):
    return file.replace(path, config.enc_mainfolder + path) + '.gpg'


def get_timestamp(file):
    if os.path.isfile(file):
        return format(os.stat(file).st_mtime)
    else:
        return 0


def get_newer(dict1, dict2, value):
    """Given two dicts, it returns the dict name which value is higher (meant for use with timestamps)
    """
    newer_value = max(dict1[value], dict2[value])
    if dict1[value] == newer_value: return dict1
    else: return dict2


def get_hash(file):
    """ Gets the checksum  and last modification time of the file                                                                                                                           
                              
    Hashlib part taken from https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    """                       
    # We'll read in 64kb chunks
    BUF_SIZE = 65536          

    # SHA1 one is enough for this
    sha1 = hashlib.sha1()     
                              
    try:                      
        with open(file, 'rb') as f:
            while True:       
                data = f.read(BUF_SIZE)
                if not data:  
                    break     
                sha1.update(data)
        file_sha1 = "{0}".format(sha1.hexdigest())
    except FileNotFoundError: 
        log.debug("File " + file + " does not exist")
        file_sha1 = ''
    except IsADirectoryError:
        log.debug("File " + file + " is a directory")
        file_sha1 = ''
                              
    return file_sha1

