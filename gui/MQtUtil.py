#
# MQt util
#
# Authors: Stijn Wopereis
# Description: util for Qt objects
#
# Copyright (c) Stijn Wopereis, 2018

import logging
logging.basicConfig()

import maya.cmds as cmds
import maya.OpenMayaUI as mui

from os.path import dirname, abspath, realpath, sep

from Qt import QtWidgets, QtCore, QtGui

import shiboken2 as shiboken

_ROOT_DIR = dirname(realpath(__file__))


def getMainWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)


def getWidgetUnderPointer():
    panel = cmds.getPanel(underPointer=True)
    if not panel:
        return None

    ptr = mui.MQtUtil.findControl(panel)
    widget = shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)
    return widget


def getWidgetByName(name):
    ptr = mui.MQtUtil.findControl(name)
    return shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)


def getPointerForWidget(widget):
    return shiboken.getCppPointer(widget)


def deleteControl(control):
    if cmds.workspaceControl(control, q=True, exists=True):
        cmds.workspaceControl(control, e=True, close=True)
        cmds.deleteUI(control, control=True)


def addControl(control, label, width):
    return cmds.workspaceControl(control, ttc=["AttributeEditor", -1], label=label)

# noinspection PyBroadException
def deleteUI(name):
    try:
        cmds.deleteUI(name)
        logger.info('removed workspace {}'.format(dialog_class.CONTROL_NAME))
    except:
        pass

# noinspection PyBroadException
def dockWindow(QtClass):
    try:
        cmds.deleteUI(QtClass.control_name)
        # logger.info('removed workspace {}'.format(dialog_class.CONTROL_NAME))
    except:
        pass

    # deleteControl(QtClass.control_name)

    # building the workspace control with maya.cmds
    main_control = addControl(QtClass.control_name, QtClass.label_name, QtClass.width)
    # conver the C++ pointer to Qt object we can use
    control_wrap = getWidgetByName(QtClass.control_name)
    # control_wrap is the widget of the docking window and now we can start working with it:
    control_wrap.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    win = QtClass(control_wrap)
    wrap_win = control_wrap.window()

    wrap_win.setWindowIcon(QtGui.QIcon(_ROOT_DIR + sep + "icon.png"))

    # after maya is ready we should restore the window since it may not be visible
    cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))

    return win.run()


def getNormalizedPath(path=""):
    return abspath(_ROOT_DIR + path)
