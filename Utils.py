#
# Utils
#
# Authors: Stijn Wopereis
# Description: main utility for the application
#
# Copyright (c) Stijn Wopereis, 2018

import maya.cmds as cmds
import logging

logging.basicConfig()


def selectHardEdges():
    cmds.selectMode(pe=True)
    cmds.polySelectConstraint(m=3, t=0x8000, sm=1)
    # reset constraint
    cmds.polySelectConstraint(m=0, t=0x8000, sm=0)


def selectSoftEdges():
    cmds.selectMode(pe=True)
    cmds.polySelectConstraint(m=3, t=0x8000, sm=2)
    # reset constraint
    cmds.polySelectConstraint(m=0, t=0x8000, sm=0)


def getSelection():
    selection = cmds.ls(selection=True, objectsOnly=True)
    return selection


def getUVSelection():
    return cmds.ls(selection=True)


def convertSelectionToUV():
    cmds.select(cmds.polyListComponentConversion(toUV=True), replace=True)


def selectObject(object):
    cmds.select(object, replace=True)


def zeroPivot():
    selection = getSelection()

    if selection is None:
        logging.info("Nothing selected!")

    for node in selection:
        __zeroPivot(node)


def resetJointOrientation():
    selection = getSelection()

    if selection is None:
        logging.info("Nothing selected!")

    for node in selection:
        __resetJointOrientation(node)


def __zeroPivot(node):
    cmds.xform(node, objectSpace=True, worldSpace=True, pivots=[0, 0, 0])


def __resetJointOrientation(node):
    cmds.joint(node, e=True, zeroScaleOrient=True, orientation=[0, 0, 0])
