#
# UDIMUtil
#
# Authors: Stijn Wopereis
# Description: utility functions for the UDIM tool
#
# Copyright (c) Stijn Wopereis, 2018

import maya.cmds as cmds
import math


class UDIMUtil:
    def __init__(self):
        self.currentU = 0.0
        self.currentV = 0.0

    def moveUVSelection(self, u, v):
        self.currentU = u
        self.currentV = v
        cmds.polyMoveUV(tu=self.currentU, tv=self.currentV)

    # @staticmethod
    def moveUV(self, u, v):
        print "U %.2f" % self.currentU
        print "V %.2f" % self.currentV
        self.moveUVSelection(u, v)

    def resetUV(self):
        upox_uvs = cmds.polyEditUVShell(query=True)

        move_u = 0
        move_v = 0
        u = [upox_uvs[i] for i in range(0, len(upox_uvs), 2)]
        v = [upox_uvs[i] for i in range(1, len(upox_uvs), 2)]

        # TODO: optimize
        for i in u:
            frac, whole = math.modf(i)
            print "we are moved by: %s on U" % whole
            if i < 0:
                move_u = abs(whole) + 1
                print "We just have to move right U by %s" % move_u
                break
            elif i > 1:
                move_u = -whole
                print "We just have to move left U by %s" % move_u
                break

        for i in v:
            frac, whole = math.modf(i)
            print "we are moved by: %s on V" % whole
            if i < 0:
                move_v = abs(whole) + 1
                print "We just have to move up V by %s" % move_v
                break
            elif i > 1:
                move_v = -whole
                print "We just have to move down V by %s" % move_v
                break

        step_u = 1
        step_v = 1
        if move_u < 0:
            step_u = -step_u
        if move_v < 0:
            step_v = -step_v

        for _ in range(int(abs(move_u))):
            self.moveUVSelection(step_u, 0)

        for _ in range(int(abs(move_v))):
            self.moveUVSelection(0, step_v)
