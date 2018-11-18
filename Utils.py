#
# Utils
#
# Authors: Stijn Wopereis
# Description: main utility for the application
#
# Copyright (c) Stijn Wopereis, 2018


import logging

logging.basicConfig()

import maya.cmds as cmds


def getSelection():
    selection = cmds.ls(sl=True, o=True)
    return selection


def selectObject(object):
    cmds.select(object)


def zeroPivot():
    selection = getSelection()

    if selection is None:
        logging.info("Nothing selected!")

    for node in selection:
        _zeroPivot(node)


def resetJointOrientation():
    selection = getSelection()

    if selection is None:
        logging.info("Nothing selected!")

    for node in selection:
        _resetJointOrientation(node)


def _zeroPivot(node):
    cmds.xform(node, os=True, ws=True, pivots=[0, 0, 0])


def _resetJointOrientation(node):
    cmds.joint(node, e=True, zso=True, o=[0, 0, 0])
