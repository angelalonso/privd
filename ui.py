#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-

from window import MyWindow as Window
import logging as log
import tools as too
               

class MyGUI():
    """ A Class managing user interaction, mainly log and debug messages
    , but supposed to manage also user feedback
    """
    def __init__(self, guimode, loglevel):
        self.loglevel = loglevel
        if guimode: self.gui = True
        else: self.gui = False

    def info(self, message):
        """ Shows info messages either at command line or in a window
        """
        if self.gui:
            Win = Window()
            Win.show_win("notification", "INFO: " + message)
        log.info(message)

    def debug(self, message):
        """ Shows debug messages
        """
        #not using windows, no one wants debug windows!
        log.debug(message)

    def ui_fileconflict(self, conflicted_file, config):
        """ Asks user to take action on a file conflict
        """
        file_local = {}
        file_remote = {}
        file_local['name'] = conflicted_file
        file_local['timestamp'] = too.beauty_timestamp('1517642665.7443795')
        file_local['size'] = too.get_filesize(conflicted_file)
        file_remote['name'] = too.get_encrypted_file_path(conflicted_file, config)
        file_remote['timestamp'] = too.beauty_timestamp('1517642675.040509')
        file_remote['size'] = '518000000000000 bytes'
        #print(Win.show_win("choices_files", title="HEYYYY", file1=file_local, file2=file_remote))
        if self.gui:
            Win = Window()
            print(Win.show_win("choices_files", title="HEYYYY", file1=file_local, file2=file_remote))
        else:
            print("No GUI")

    # TODO: move to tools when all functions related to files have been moved to files.py
    def tmp_timestamp(self, timestamp):
        """ returns a readable version of a timestamp
        """
        beauty = datetime.datetime.fromtimestamp(
                float(timestamp)).strftime('%d-%m-%Y %H:%M:%S')
        return beauty

