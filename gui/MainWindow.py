#
# MainWindow
#
# Authors: Stijn Wopereis
# Description: main window widget for the application
#
# Copyright (c) Stijn Wopereis, 2018

import maya.cmds as cmds
from PySide2 import QtCore, QtGui, QtWidgets

from os.path import dirname, abspath, realpath, sep

# Custom
from gui.ToolWindow import ToolWindow
from gui.UDIMWindow import UDIMWindow

_ROOT_DIR = dirname(realpath(__file__))


class MainWindow(QtWidgets.QMainWindow):
    label_name = 'AutoTools by Wopster'
    control_name = 'autotools_control'
    width = 300

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = parent
        self.window_name = 'autotools'

        self.setWindowIcon(QtGui.QIcon(_ROOT_DIR + sep + "icons/icon.png"))

        # self.main_layout = parent.layout()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(0)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName(self.window_name)
        self.setWindowTitle(self.label_name)
        self.setProperty("saveWindowPref", True)

        # Init full UI
        self.init()

        # Main widget
        # self.widget = QtWidgets.QWidget()
        # self.setCentralWidget(self.widget)
        #
        # window = QtWidgets.QMainWindow()
        # window.setWindowTitle('Frame Widget Test')
        #
        # frame = FrameWidget('Frame Title', window)
        #
        # widget = QtWidgets.QWidget(frame)
        # layout = QtWidgets.QVBoxLayout(widget)
        # layout.setSpacing(0)
        # layout.setContentsMargins(2, 2, 2, 2)
        #
        # widget.setLayout(layout)
        # frame.setLayout(layout)
        #
        # for i in range(5):
        #     layout.addWidget(QtWidgets.QPushButton('Button %s' % i, widget))
        #
        # # window.setCentralWidget(frame)
        # self.setCentralWidget(self.toolWindow)
        #
        # self.main_layout.addWidget(self.toolWindow)
        # self.widget.setLayout(self.main_layout)

    def init(self):
        self.create_menu()
        self.create_widgets()
        self.create_layouts()

    def create_menu(self):
        bar = self.menuBar()
        # Create Root Menus
        file = bar.addMenu('Object')
        edit = bar.addMenu('Help')

    def create_widgets(self):
        self.tool_window_widget = QtWidgets.QWidget()
        self.tool_window = ToolWindow(self)
        self.udim_window = UDIMWindow(self)

        self.tab_control = QtWidgets.QTabWidget()
        self.tab_control.addTab(self.tool_window, "Utils")
        self.tab_control.addTab(self.udim_window, "UDIM")

    def create_layouts(self):
        # layout = QtWidgets.QVBoxLayout(self.tool_window_widget)
        # self.tool_window_widget.setLayout(layout)
        self.setCentralWidget(self.tab_control)

    def run(self):
        return self
