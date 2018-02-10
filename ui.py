#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-

import logging as log    
from window import MyWindow as Window
               
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

    def ui_fileconflict(self, file):
        """ Asks user to take action on a file conflict
        """
        if self.gui:
            print("No GUI")
        else:
            print("GUI")


