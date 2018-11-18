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

from Utils import getSelection, selectObject


class UDIMUtil:
    def __init__(self):
        self.current_u = 0.0
        self.current_v = 0.0

    def moveUVSelection(self, u, v):
        cmds.polyMoveUV(tu=u, tv=v)

    def moveUV(self, u, v):
        selection = getSelection()

        if selection is None:
            return

        logging.info("move U by %s" % u)
        logging.info("move V by %s" % v)

        for object in selection:
            # Focus on current object
            selectObject(object)
            self.moveUVSelection(u, v)

    def resetUVOnObject(self, uvs, object):
        move_u = 0
        move_v = 0

        u = [uvs[i] for i in range(0, len(uvs), 2)]
        v = [uvs[i] for i in range(1, len(uvs), 2)]

        # TODO: optimize
        for i in u:
            frac, whole = math.modf(i)
            # logging.info("we are moved by: %s on U" % whole)
            if i < 0:
                move_u = abs(whole) + 1
                logging.info("We just have to move right U by %s" % move_u)
                break
            elif i > 1:
                move_u = -whole
                logging.info("We just have to move left U by %s" % move_u)
                break

        for i in v:
            frac, whole = math.modf(i)
            # logging.info("we are moved by: %s on V" % whole)
            if i < 0:
                move_v = abs(whole) + 1
                logging.info("We just have to move up V by %s" % move_v)
                break
            elif i > 1:
                move_v = -whole
                logging.info("We just have to move down V by %s" % move_v)
                break

        step_u = 1
        step_v = 1
        if move_u < 0:
            step_u = -step_u
        if move_v < 0:
            step_v = -step_v

        #  Focus on current object
        selectObject(object)
        for _ in range(int(abs(move_u))):
            self.moveUVSelection(step_u, 0)

        for _ in range(int(abs(move_v))):
            self.moveUVSelection(0, step_v)

    def resetUVOnSelection(self):
        selection = getSelection()

        if selection is None:
            return

        for object in selection:
            uv_amount = cmds.polyEvaluate(object, uv=True)

            if uv_amount:
                for uv in range(uv_amount):
                    uvs = cmds.polyEditUVShell("%s.map[%d]" % (object, uv), q=True)
                    self.resetUVOnObject(object=object, uvs=uvs)
        # Add selection back to perform next functions
        selectObject(selection)
