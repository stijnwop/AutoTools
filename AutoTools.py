#
# Auto Tools
#
# Authors: Stijn Wopereis
# Description: Main class for the auto tools
#
# Copyright (c) Stijn Wopereis, 2018


import inspect
import sys

from gui.MainWindow import MainWindow
from gui.MQtUtil import getMainWindow, getPointerForWidget

from os.path import dirname

import logging

logging.basicConfig()

_ROOT_DIR = dirname(__file__)


class AutoTool:

    def __init__(self):
        self.main_window = MainWindow(getMainWindow())
        self.main_window.show()

    def delete(self):
        if not self.main_window is None:
            self.main_window.deleteLater()


def resetSessionForScript(userPath=None):
    if userPath is None:
        userPath = _ROOT_DIR

    userPath = userPath.lower()

    print(userPath)
    toDelete = []

    for key, module in sys.modules.iteritems():
        try:
            moduleFilePath = inspect.getfile(module).lower()

            logging.info("Current %s" % __file__.lower())

            if moduleFilePath == __file__.lower():
                continue

            if moduleFilePath.startswith(userPath):
                logging.info("Removing %s" % key)
                toDelete.append(key)
        except:
            pass

    for module in toDelete:
        del (sys.modules[module])


try:
    main.delete()
except NameError as e:
    pass

main = AutoTool()
