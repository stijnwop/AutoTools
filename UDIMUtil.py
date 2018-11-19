#
# UDIMUtil
#
# Authors: Stijn Wopereis
# Description: utility functions for the UDIM tool
#
# Copyright (c) Stijn Wopereis, 2018

import maya.cmds as cmds
import math
import logging

logging.basicConfig()

from Utils import convertSelectionToUV, selectObject, getUVSelection, getSelection


class UDIMUtil:
    def __init__(self):
        self.current_u = 0.0
        self.current_v = 0.0

    def moveUVOnMap(self, map, u, v):
        cmds.polyEditUV(map, uValue=u, vValue=v)

    def moveUVOnSelection(self, u, v):
        selection_buffer = []
        objects = getSelection()

        if objects is None:
            return

        for object in objects:
            selectObject(object)
            convertSelectionToUV()
            upox = getUVSelection()

            if upox is None:
                return

            self.moveUVOnMap(upox, u, v)
            selection_buffer.append(upox)

        if selection_buffer:
            for selection in selection_buffer:
                cmds.select(selection, add=True)

    def moveUVToZeroSpace(self, map, uvs):
        # Todo: replace this with a faster approach
        u = [uvs[i] for i in range(0, len(uvs), 2)]
        v = [uvs[i] for i in range(1, len(uvs), 2)]

        move_u = 0
        move_v = 0

        for i in u:
            _, whole = math.modf(i)
            # logging.info("we are moved by: %s on U" % whole)
            if i < 0:
                move_u = abs(whole) + 1
                break
            elif i > 1:
                move_u = -whole
                break

        for i in v:
            _, whole = math.modf(i)
            # logging.info("we are moved by: %s on V" % whole)
            if i < 0:
                move_v = abs(whole) + 1
                break
            elif i > 1:
                move_v = -whole
                break

        self.moveUVOnMap(map, move_u, move_v)

    def processUVReset(self):
        selection_buffer = []
        objects = getSelection()

        if objects is None:
            return

        for object in objects:
            selectObject(object)
            convertSelectionToUV()
            upox = getUVSelection()

            if upox is None:
                return

            uvs = cmds.polyEditUVShell(upox, query=True)
            self.moveUVToZeroSpace(upox, uvs)
            selection_buffer.append(upox)

        if selection_buffer:
            for selection in selection_buffer:
                cmds.select(selection, add=True)

    def resetUVOnSelection(self):
        self.processUVReset()
