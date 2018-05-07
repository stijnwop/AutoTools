#
# MainWindow
#
# Authors: Stijn Wopereis
# Description: main window widget for the application
#
# Copyright (c) Stijn Wopereis, 2018

import os
from Qt import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwds):
        super(MainWindow, self).__init__(*args, **kwds)

        # self.parent = parent
        self.window_name = 'AutoToolsMain'

        # Set basic window properties
        self.setWindowTitle('AutoTools')
        self.setObjectName(self.window_name)

        if os.name == 'nt':  # windows platform
            self.setWindowFlags(QtCore.Qt.Window)
        else:
            self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)

        self.setProperty("saveWindowPref", True)  # maya's automatic window management

        # Define window dimensions
        self.setMinimumWidth(400)
        self.setMaximumWidth(800)
        self.setMinimumHeight(400)
        self.setMaximumHeight(800)

        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(8, 8, 8, 8)
        self.setCentralWidget(self.central_widget)
