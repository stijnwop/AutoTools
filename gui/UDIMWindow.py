#
# UDIMWindow
#
# Authors: Stijn Wopereis
# Description: dialog widget for the UDIM tool
#
# Copyright (c) Stijn Wopereis, 2018

from PySide2 import QtCore, QtGui, QtWidgets

from UDIMUtil import UDIMUtil

from functools import partial


class UDIMWindow(QtWidgets.QDialog):
    PREDEFINED_MATS = [
        {'id': "00", 'name': "Painted metal", 'u': 0, 'v': 0},
        {'id': "01", 'name': "Painted Plastic", 'u': 1, 'v': 0},
        {'id': "02", 'name': "Chrome", 'u': 2, 'v': 0},
        {'id': "03", 'name': "Copper", 'u': 3, 'v': 0},
        {'id': "04", 'name': "Galvanized metal", 'u': 4, 'v': 0},
        {'id': "05", 'name': "Rubber", 'u': 5, 'v': 0},
        {'id': "06", 'name': "Painted metal old", 'u': 6, 'v': 0},
        {'id': "07", 'name': "Fabric", 'u': 7, 'v': 0},
        {'id': "08", 'name': "Silver scratched", 'u': 0, 'v': 1},
        {'id': "09", 'name': "Silver bumpy", 'u': 1, 'v': 1},
        {'id': "10", 'name': "Fabric 1", 'u': 2, 'v': 1},
        {'id': "11", 'name': "Fabric 2", 'u': 3, 'v': 1},
        {'id': "12", 'name': "Leather 1", 'u': 4, 'v': 1},
        {'id': "13", 'name': "Leather 2", 'u': 5, 'v': 1},
        {'id': "14", 'name': "Wood", 'u': 6, 'v': 1},
        {'id': "15", 'name': "Dirt", 'u': 7, 'v': 1},
        {'id': "16", 'name': "Painted metal", 'u': 0, 'v': 2},
        {'id': "17", 'name': "Painted plastic", 'u': 1, 'v': 2},
        {'id': "18", 'name': "Silver rough", 'u': 2, 'v': 2},
        {'id': "19", 'name': "Brass scratched", 'u': 3, 'v': 2},
        {'id': "20", 'name': "Reflector white", 'u': 4, 'v': 2},
        {'id': "21", 'name': "Reflector red", 'u': 5, 'v': 2},
        {'id': "22", 'name': "Reflector yellow", 'u': 6, 'v': 2},
        {'id': "23", 'name': "Reflector daylight", 'u': 7, 'v': 2},
        {'id': "24", 'name': "Gear-shift stick plastic", 'u': 0, 'v': 3},
        {'id': "25", 'name': "Leather 3", 'u': 1, 'v': 3},
        {'id': "26", 'name': "Perforated syntetic fabric", 'u': 2, 'v': 3},
        {'id': "27", 'name': "Glass clear", 'u': 3, 'v': 3},
        {'id': "28", 'name': "Glass square", 'u': 4, 'v': 3},
        {'id': "29", 'name': "Glass line", 'u': 5, 'v': 3},
    ]

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
            button.clicked.connect(partial(self.resetUVOnSelection, i, -1))
            if i >= amount_of_color_buttons / 2:
                self.colors_b_layout_box.addWidget(button)
            else:
                self.colors_t_layout_box.addWidget(button)

        self.colors_layout_grid.addLayout(self.colors_t_layout_box, 0, 0)
        self.colors_layout_grid.addLayout(self.colors_b_layout_box, 1, 0)

        self.predefined_mats_scroll = QtWidgets.QScrollArea()
        self.predefined_mats_scroll.setWidgetResizable(True)

        widget = QtWidgets.QWidget(self.predefined_mats_scroll)
        layout = QtWidgets.QFormLayout(self.predefined_mats_scroll)
        layout.setSpacing(2)
        layout.setAlignment(QtCore.Qt.AlignTop)

        for index, mat in enumerate(self.PREDEFINED_MATS):
            mat_button = QtWidgets.QPushButton(" %s - %s" % (mat["id"], mat["name"]), self.predefined_mats_scroll)
            mat_button.clicked.connect(partial(self.resetUVOnSelection, mat["u"], mat["v"]))
            mat_button.setMinimumHeight(30)
            mat_button.setStyleSheet("QPushButton { text-align: left; }")
            layout.addRow(mat_button)

        widget.setLayout(layout)
        self.predefined_mats_scroll.setWidget(widget)

        # layout.addStretch()
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

    def resetUVOnSelection(self, u, v):
        self.udimUtil.resetUVOnSelection()
        self.udimUtil.moveUV(u, v)
