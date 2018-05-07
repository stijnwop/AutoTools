#
# Auto Tools
#
# Authors: Stijn Wopereis
# Description: Main class for the auto tools
#
# Copyright (c) Stijn Wopereis, 2018


import inspect
import sys

from os.path import dirname

from gui.MainWindow import MainWindow
from gui.MQtUtil import getMainWindow

ROOT_DIR = dirname(__file__)


class AutoTool:

    def __init__(self):
        main = MainWindow()
        main.show()
        

def resetSessionForScript(userPath=None):
    if userPath is None:
        userPath = ROOT_DIR

    userPath = userPath.lower()

    toDelete = []

    for key, module in sys.modules.iteritems():
        try:
            moduleFilePath = inspect.getfile(module).lower()

            if moduleFilePath == __file__.lower():
                continue

            if moduleFilePath.startswith(userPath):
                print("Removing %s" % key)
                toDelete.append(key)
        except:
            pass

    for module in toDelete:
        del (sys.modules[module])
