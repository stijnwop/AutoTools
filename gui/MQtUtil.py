#
# MQt util
#
# Authors: Stijn Wopereis
# Description: util for Qt objects
#
# Copyright (c) Stijn Wopereis, 2018

import maya.cmds as cmds
import maya.OpenMayaUI as mui

from Qt import QtCore

import shiboken2 as shiboken


def getMainWindow():
    ptr = mui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(ptr), QtCore.QObject)


def getWidgetUnderPointer():
    panel = cmds.getPanel(underPointer=True)
    if not panel:
        return None

    ptr = mui.MQtUtil.findControl(panel)
    widget = shiboken.wrapInstance(long(ptr), QtCore.QObject)
    return widget


def getWidgetByName(name):
    ptr = mui.MQtUtil.findControl(name)
    widget = shiboken.wrapInstance(long(ptr), QtCore.QObject)
    return widget


def getPointerForWidget(widget):
    return shiboken.getCppPointer(widget)
