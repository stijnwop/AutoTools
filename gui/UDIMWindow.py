#
# UDIMWindow
#
# Authors: Stijn Wopereis
# Description: dialog widget for the UDIM tool
#
# Copyright (c) Stijn Wopereis, 2018

from PySide2 import QtCore, QtWidgets

from UDIMUtil import UDIMUtil

from functools import partial


class UDIMWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(UDIMWindow, self).__init__(parent)

        self.udimUtil = UDIMUtil()

        self.window_name = 'autotools_udimwindow'
        self.setObjectName(self.window_name)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)

        self.colors_label = QtWidgets.QLabel(" Material RGB indexes")
        self.predefined_label = QtWidgets.QLabel(" Predefined materials")
        self.mover_label = QtWidgets.QLabel(" Move on UV grid")

        self.colors_layout_grid = QtWidgets.QGridLayout(self)
        self.colors_t_layout_box = QtWidgets.QHBoxLayout(self)
        self.colors_b_layout_box = QtWidgets.QHBoxLayout(self)

        self.colors_layout_grid.setSpacing(2)
        self.colors_t_layout_box.setSpacing(2)
        self.colors_b_layout_box.setSpacing(2)

        self.color_buttons = []

        amount_of_color_buttons = 8
        for i in range(amount_of_color_buttons):
            button = QtWidgets.QPushButton("Index - %s" % i, self)
            button.clicked.connect(partial(self.presetUV, i, -1))
            if i >= amount_of_color_buttons / 2:
                self.colors_b_layout_box.addWidget(button)
            else:
                self.colors_t_layout_box.addWidget(button)

        self.colors_layout_grid.addLayout(self.colors_t_layout_box, 0, 0)
        self.colors_layout_grid.addLayout(self.colors_b_layout_box, 1, 0)

        self.predefined_mats = [
            "Painted metal",
            "Painted Plastic",
            "Chrome",
            "Copper",
            "Galvanized metal",
            "Rubber",
            "Painted metal old",
            "Fabric",
            "Silver scratched",
            "Silver bumpy",
            "Fabric 1",
            "Fabric 2",
            "Leather 1",
            "Leather 2",
            "Wood",
            "Dirt",
            "Painted metal",
            "Painted plastic",
            "Silver rough",
            "Brass scratched",
            "Reflector white",
            "Reflector red",
            "Reflector yellow",
            "Reflector daylight",
            "Gear-shift stick plastic",
            "Leather 3",
            "Perforated syntetic fabric",
            "Glass clear",
            "Glass square",
            "Glass line"
        ]

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(widget)
        layout.setSpacing(2)
        layout.setAlignment(QtCore.Qt.AlignTop)

        for index, mat in enumerate(self.predefined_mats):
            mat_button = QtWidgets.QPushButton(" %s - %s" % (index, mat), widget)
            mat_button.setMinimumHeight(30)
            mat_button.setStyleSheet("QPushButton { text-align: left; }")
            layout.addWidget(mat_button)
        # TODO: optimize

        self.predefined_mats_scroll = QtWidgets.QScrollArea(self)
        widget.setLayout(layout)
        self.predefined_mats_scroll.setWidget(widget)

        self.mover_layout_grid = QtWidgets.QGridLayout(self)
        self.mover_layout_first_box = QtWidgets.QHBoxLayout(self)
        self.mover_layout_second_box = QtWidgets.QHBoxLayout(self)
        self.mover_layout_third_box = QtWidgets.QHBoxLayout(self)

        self.button_move_up = QtWidgets.QPushButton("up")
        self.button_move_down = QtWidgets.QPushButton("down")
        self.button_move_left = QtWidgets.QPushButton("left")
        self.button_move_right = QtWidgets.QPushButton("right")

        self.button_move_up.clicked.connect(lambda: self.moveUV(0, 1))
        self.button_move_down.clicked.connect(lambda: self.moveUV(0, -1))
        self.button_move_left.clicked.connect(lambda: self.moveUV(-1, 0))
        self.button_move_right.clicked.connect(lambda: self.moveUV(1, 0))

        self.mover_layout_first_box.addWidget(self.button_move_up)
        self.mover_layout_third_box.addWidget(self.button_move_down)
        self.mover_layout_second_box.addWidget(self.button_move_left)
        self.mover_layout_second_box.addWidget(self.button_move_right)

        self.mover_layout_grid.addLayout(self.mover_layout_first_box, 0, 0)
        self.mover_layout_grid.addLayout(self.mover_layout_second_box, 1, 0)
        self.mover_layout_grid.addLayout(self.mover_layout_third_box, 2, 0)

        self.main_layout.addWidget(self.colors_label)
        self.main_layout.addLayout(self.colors_layout_grid)
        self.main_layout.addWidget(self.predefined_label)
        self.main_layout.addWidget(self.predefined_mats_scroll)
        self.main_layout.addWidget(self.mover_label)
        self.main_layout.addLayout(self.mover_layout_grid)

    def moveUV(self, u, v):
        self.udimUtil.moveUV(u, v)

    def presetUV(self, u, v):
        self.udimUtil.resetUV()
        self.udimUtil.moveUV(u, v)
