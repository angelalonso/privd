import glob
import logging as log
import os
import subprocess
import sys
import time

from files import File as File
from tools import real2homeenv_path as getenvhome
from tools import homeenv2real_path as getrealhome
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
    # TODO: probably get rid of the whole syncer thing if it can be moved to status altogether

    def __init__(self, config, key):
        """ Checks that everything is coherent between local and remote(encrypted) copies
        """
        self.config = config
        self.config.key = key

        self.status = Status(self.config)

        if not os.path.exists(getrealhome(self.config.enc_mainfolder)):
            log.debug("Encrypted Main Folder does not exist, creating " + getrealhome(self.config.enc_mainfolder))
            os.makedirs(getrealhome(self.config.enc_mainfolder))

    def daemon(self):
        self.status.read_local()
        self.status.read_remote()
        #self.status.first_sync()
        self.status.syncer()


