#
# ToolWindow
#
# Authors: Stijn Wopereis
# Description: dialog widget for the helper tools
#
# Copyright (c) Stijn Wopereis, 2018

from PySide2 import QtCore, QtGui, QtWidgets

import maya.cmds as cmds

import MQtUtil

from Utils import zeroPivot, resetJointOrientation, selectHardEdges, selectSoftEdges
from os.path import dirname, realpath, sep

_ROOT_DIR = dirname(realpath(__file__))


class ToolWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(ToolWindow, self).__init__(parent)

        self.window_name = 'autotools_toolwindow'
        self.UI_FRAME_LAYOUT_CLUSTER = 'UI_FRAME_LAYOUT_CLUSTER'
        self.setObjectName(self.window_name)

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setAlignment(QtCore.Qt.AlignTop)

        self.snapPivot = QtWidgets.QCheckBox("Snap pivot")
        self.ignoreJointSelection = QtWidgets.QCheckBox("Ignore joint on DRAG")

        self.quickAccessLabel = QtWidgets.QLabel(" Quick access")

        self.quickAccessLayoutGrid = QtWidgets.QGridLayout()
        self.quickAccessLayoutReset = QtWidgets.QHBoxLayout()
        self.quickAccessLayoutFix = QtWidgets.QHBoxLayout()
        self.quickAccessLayoutEdges = QtWidgets.QHBoxLayout()
        self.quickAccessLayoutGrid.setSpacing(2)
        self.quickAccessLayoutReset.setSpacing(2)
        self.quickAccessLayoutFix.setSpacing(2)
        self.quickAccessLayoutEdges.setSpacing(2)

        self.resetPivotToZero = QtWidgets.QPushButton("ResetPivotToZero", self)
        self.resetJointOrientation = QtWidgets.QPushButton("ResetJointOrientation", self)
        self.presetRadius = QtWidgets.QPushButton("PresetRadius", self)
        self.compensate = QtWidgets.QPushButton("Compensate", self)
        self.hardEdges = QtWidgets.QPushButton("SelectHardEdges", self)
        self.softEdges = QtWidgets.QPushButton("SelectSoftEdges", self)

        self.resetPivotToZero.clicked.connect(lambda: zeroPivot())
        self.resetJointOrientation.clicked.connect(lambda: resetJointOrientation())
        self.hardEdges.clicked.connect(lambda: selectHardEdges())
        self.softEdges.clicked.connect(lambda: selectSoftEdges())

        self.resetPivotToZero.setStyleSheet("QPushButton { text-align: left; }")
        self.resetJointOrientation.setStyleSheet("QPushButton { text-align: left; }")
        self.presetRadius.setStyleSheet("QPushButton { text-align: left; }")
        self.compensate.setStyleSheet("QPushButton { text-align: left; }")
        self.hardEdges.setStyleSheet("QPushButton { text-align: left; }")
        self.softEdges.setStyleSheet("QPushButton { text-align: left; }")

        self.resetPivotToZero.setMinimumHeight(30)
        self.resetJointOrientation.setMinimumHeight(30)
        self.presetRadius.setMinimumHeight(30)
        self.compensate.setMinimumHeight(30)
        self.hardEdges.setMinimumHeight(30)
        self.softEdges.setMinimumHeight(30)

        self.resetPivotToZero.setIcon(QtGui.QIcon(_ROOT_DIR + sep + "icons/icon_reset.png"))
        self.resetJointOrientation.setIcon(QtGui.QIcon(_ROOT_DIR + sep + "icons/icon_reset.png"))
        self.presetRadius.setIcon(QtGui.QIcon(_ROOT_DIR + sep + "icons/icon_radius.png"))
        self.compensate.setIcon(QtGui.QIcon(_ROOT_DIR + sep + "icons/icon.png"))

        self.quickAccessLayoutReset.addWidget(self.resetPivotToZero)
        self.quickAccessLayoutReset.addWidget(self.resetJointOrientation)
        self.quickAccessLayoutFix.addWidget(self.presetRadius)
        self.quickAccessLayoutFix.addWidget(self.compensate)
        self.quickAccessLayoutEdges.addWidget(self.hardEdges)
        self.quickAccessLayoutEdges.addWidget(self.softEdges)

        self.quickAccessLayoutGrid.addLayout(self.quickAccessLayoutEdges, 2, 0)
        self.quickAccessLayoutGrid.addLayout(self.quickAccessLayoutReset, 0, 0)
        self.quickAccessLayoutGrid.addLayout(self.quickAccessLayoutFix, 1, 0)

        MQtUtil.deleteUI(self.UI_FRAME_LAYOUT_CLUSTER)

        # Parent it to this QDialog
        cmds.setParent(self.window_name)
        layout = cmds.frameLayout(self.UI_FRAME_LAYOUT_CLUSTER, label='Skincluster generation', cll=True, mh=2, mw=2)

        qFrameLayout = MQtUtil.getWidgetByName(layout)
        qFrameLayout.event = None
        qLayout = QtWidgets.QVBoxLayout(qFrameLayout)
        # qLayout.addWidget(jointTitl2e)
        qFrameLayout.setLayout(qLayout)

        # self.mainLayout.addLayout(qLayout)

        # self.jointTitle = QtWidgets.QLabel(" Influences(Binding Joints)")
        # self.jointTitle.setStyleSheet("color: white;background-color: black;")
        # self.jointTitle.setFixedSize(300, 30)
        # self.jointList = QtWidgets.QListWidget(self)
        # self.jointList.resize(300, 300)
        # for i in range(10):
        #     self.jointList.addItem('Item %s' % (i + 1))
        #
        # self.skinTitle = QtWidgets.QLabel(" Current Skin Weights")
        # self.skinTitle.setStyleSheet("color: white;background-color: black;")
        # self.skinTitle.setFixedSize(300, 30)
        #
        # self.displayInfLabel1 = QtWidgets.QLabel("Inf1");
        # self.displayInfLabel2 = QtWidgets.QLabel("Inf2");
        # self.displayInfLabel3 = QtWidgets.QLabel("Inf3");
        # self.displayInfLabel4 = QtWidgets.QLabel("Inf4");
        #
        # self.infLabelLayout = QtWidgets.QHBoxLayout()
        # self.infLabelLayout.addWidget(self.displayInfLabel1)
        # self.infLabelLayout.addWidget(self.displayInfLabel2)
        # self.infLabelLayout.addWidget(self.displayInfLabel3)
        # self.infLabelLayout.addWidget(self.displayInfLabel4)
        #
        # self.displayWeight1 = QtWidgets.QLineEdit("0");
        # self.displayWeight2 = QtWidgets.QLineEdit("0");
        # self.displayWeight3 = QtWidgets.QLineEdit("0");
        # self.displayWeight4 = QtWidgets.QLineEdit("0");
        #
        # self.weightLayout = QtWidgets.QHBoxLayout()
        # self.weightLayout.addWidget(self.displayWeight1)
        # self.weightLayout.addWidget(self.displayWeight2)
        # self.weightLayout.addWidget(self.displayWeight3)
        # self.weightLayout.addWidget(self.displayWeight4)
        #
        # self.skinWeightGrid = QtWidgets.QGridLayout()
        # self.skinWeightGrid.addLayout(self.infLabelLayout, 0, 0)
        # self.skinWeightGrid.addLayout(self.weightLayout, 1, 0)
        #
        # self.name = QtWidgets.QCheckBox("Name")
        # self.color = QtWidgets.QCheckBox("Color")
        # self.position = QtWidgets.QCheckBox("Position")
        # self.rotation = QtWidgets.QCheckBox("Rotation")
        #
        # self.runButton = QtWidgets.QPushButton("Assign")
        #
        #
        self.mainLayout.addWidget(self.quickAccessLabel)
        self.mainLayout.addLayout(self.quickAccessLayoutGrid)
        self.mainLayout.addWidget(self.snapPivot)
        self.mainLayout.addWidget(self.ignoreJointSelection)
        self.mainLayout.addWidget(qFrameLayout)
        #
        # self.mainLayout.addWidget(self.jointTitle)
        # self.mainLayout.addWidget(self.jointList)
        # self.mainLayout.addWidget(self.skinTitle)
        # self.mainLayout.addLayout(self.skinWeightGrid)
        # self.mainLayout.addWidget(self.name)
        # self.mainLayout.addWidget(self.color)
        # self.mainLayout.addWidget(self.position)
        # self.mainLayout.addWidget(self.runButton)
