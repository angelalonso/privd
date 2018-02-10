#!/usr/bin/python3                                                                                                                                                                              
# -*- coding: utf-8 -*-


import subprocess
import argparse
import logging as log
import os
import time


from tools import homeenv2real_path as getrealhome
from tools import homeenv2real_path as home2real
from tools import get_filesize as getsize
from tools import beauty_timestamp
from configs import Config
from ui import MyGUI as Gui
from keys import Key as Key
from status import Status
from window import MyWindow as Window


def importer(key):
    """ Imports GPG keys and config file from a folder
    """
    # TODO: manage errors when files are not found
    import_folder = "importexport"
    gui.debug("Importing files from a different machine")
    confirmed = False
    while not confirmed:
        print("Do you want to import from folder " + import_folder + "? ")
        confirmation = input("[y/n] ").lower()
        if confirmation == "y":
            confirmed = True
        elif confirmation == "n":
            import_folder = input("Choose new path to import from: ")
    config.import_file(import_folder)
    key.import_all(import_folder)
    status.sync_from_remote()


def exporter(key):
    """ Exports GPG keys and config file from a folder
    """
    export_folder = "importexport"
    gui.debug("Exporting files for use on a different machine")
    confirmed = False
    while not confirmed:
        print("Do you want to export to folder " + export_folder + "? ")
        confirmation = input("[y/n] ").lower()
        if confirmation == "y":
            confirmed = True
        elif confirmation == "n":
            export_folder = input("Choose new path to export to: ")
        if confirmed:
            if not os.path.exists(export_folder):
                os.makedirs(export_folder)
    config.export_file(export_folder)
    key.export_all(export_folder)


def backup_local(config):
    """ Creates a local backup of the local folder
    """
    for folder in config.folders:
        folder_path = getrealhome(folder['path'])
        backup_path = folder_path + ".backup"
        gui.debug("Backing up from " + folder_path + " to " + backup_path)
        if not os.path.exists(backup_path):
            gui.debug(backup_path + " does not exist, creating")
            os.makedirs(backup_path)
        cmd = 'rsync -av ' + folder_path + '/ ' + backup_path
        cmd_run = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True) 


def empty_safety(daemon):
    """ Asks for confirmation when the local folder is empty
    """
    print("ATTENTION! Your local folder is empty")
    print("If you continue, you'll delete the remote files as well")
    print(" - [r]emove remote files as well")
    print(" - [o]verwrite local files with the remote ones")
    print(" - [c]ancel privd daemon")
    answer = ""
    while answer not in ["r", "o", "c"]:
        answer = input("Please confirm what to do next [r/o/c] ->").lower()
        if answer == "o":
            status.sync_from_remote()
        elif answer == "c":
            daemon = False
    return daemon


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Show higher level of verbosity', required=False, action='store_true')
    parser.add_argument('-g', '--graphical', help='Interact using graphical interfaces instead of console', required=False, action='store_true')
    parser.add_argument('-i', '--import', help='Import configuration before running the algorythm', required=False, action='store_true')
    parser.add_argument('-e', '--export', help='Export configuration for use on a different machine', required=False, action='store_true')
    parser.add_argument('-s', '--single', help='Run the sync algorythm once', required=False, action='store_true')
    parser.add_argument('-t', '--test', help='Run the test', required=False, action='store_true')

    args = vars(parser.parse_args())
    if args['verbose']:
        log.basicConfig(format="%(levelname)s: %(asctime)s %(message)s", level=log.DEBUG)
        loglevel = "debug"
    else:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
        loglevel = "info"

    config = Config(args['graphical'], loglevel)
    gui = Gui(args['graphical'], loglevel)
    key = Key(config.key_email, gui)
    status = Status(config, key)


    if args['import']:
        importer(key)
    else:
        if args['export']:
            exporter(key)
        elif args['single']:
            gui.debug("Single run at " + str(int(time.time())) + " - " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) )
            status.check_n_sync()
        # TODO: move this to where it can be needed: file conflicts. Start with informational dialogs on changes
        elif args['test']:
            Win = Window()
            #print(Win.show_win("true_false", "You know what happens with a Hello world"))
            file_local = {}
            file_remote = {}
            file_local['name'] = '$HOME/Private/testfile'
            file_local['timestamp'] = beauty_timestamp('1517642665.7443795')
            file_local['size'] = getsize('$HOME/Private/testfile')
            file_remote['name'] = 'HOME/Private/testfile'
            file_remote['timestamp'] = beauty_timestamp('1517642675.040509')
            file_remote['size'] = '518000000000000 bytes'
            print(Win.show_win("choices_files", title="HEYYYY", file1=file_local, file2=file_remote))
        else:
            daemon = True
            if status.read_local() == 0 and status.read_remote() != 0:
                daemon = empty_safety(daemon)
            while daemon == True:
                gui.debug("New run at " + str(int(time.time())) + " - " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) )
                status.check_n_sync()
                # BACKUP ONLY WHILE I TEST
                backup_local(config)
                TIMEOUT = 5
                try:
                    for i in range(0, TIMEOUT):
                        time.sleep(1)
                except KeyboardInterrupt:
                    daemon = False
            print("Exiting gracefully...")
