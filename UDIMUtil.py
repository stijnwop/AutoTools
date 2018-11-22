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

from Utils import convertSelectionToUV, selectObject, getUVSelection


class UDIMUtil:
    def __init__(self):
        self.selection_buffer = []

    def __selectBuffer(self):
        if self.selection_buffer:
            for selection in self.selection_buffer:
                cmds.select(selection, add=True)

    def __moveUVOnMap(self, map, u, v):
        cmds.polyEditUV(map, uValue=u, vValue=v)

    def moveUVOnSelection(self, u, v):
        self.selection_buffer = []
        objects = getUVSelection()

        if objects is None:
            return

        convertSelectionToUV()
        upox = getUVSelection()

        if upox is None:
            return

        self.__moveUVOnMap(upox, u, v)
        self.selection_buffer.append(upox)

        self.__selectBuffer()

    def __moveUVToZeroSpace(self, map, uvs):
        u = uvs[::2]
        v = uvs[1::2]

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

        self.__moveUVOnMap(map, move_u, move_v)

    def resetUVOnSelection(self):
        self.selection_buffer = []
        objects = getUVSelection()

        if objects is None:
            return

        for object in objects:
            selectObject(object)
            convertSelectionToUV()
            upox = getUVSelection()

            if upox is None:
                return

            uvs = cmds.polyEditUVShell(upox, query=True)
            self.__moveUVToZeroSpace(upox, uvs)
            self.selection_buffer.append(upox)

        self.__selectBuffer()
