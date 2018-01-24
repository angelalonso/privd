#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-

#  ====  Automated Import and pip-installation of requirements  ====  #
import subprocess             
                              
def pipinstall(package):      
    subprocess.call(['pip3', 'install', '--user', package])                                                                                                                                           
               
try: import logging as log    
except ImportError:           
    pipinstall('logging')     
    import logging as log     
               

from window import MyWindow as Window


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
