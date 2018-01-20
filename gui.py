#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-

from window import MyWindow as Window
import logging as log

class MyGUI():
    def __init__(self, guimode, loglevel):
        self.loglevel = loglevel
        if guimode: self.gui = True
        else: self.gui = False

    def info(self, message):
        if self.gui:
            Win = Window()
            Win.show_win("notification", "INFO: " + message)
        log.info(message)

    def debug(self, message):
        #not using windows, no one wants debug windows!
        log.debug(message)
