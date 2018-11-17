from PySide2 import QtCore, QtWidgets

import maya.cmds as cmds

import MQtUtil


class UDIMWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(UDIMWindow, self).__init__(parent)

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
            button = QtWidgets.QPushButton("Mat index %s" % i, self)
            if i >= amount_of_color_buttons / 2:
                self.colors_b_layout_box.addWidget(button)
            else:
                self.colors_t_layout_box.addWidget(button)

        self.colors_layout_grid.addLayout(self.colors_t_layout_box, 0, 0)
        self.colors_layout_grid.addLayout(self.colors_b_layout_box, 1, 0)

        self.predefined_buttons = []

        # Need to define it like this cause it will change names
        self.button_00 = QtWidgets.QPushButton("00")
        self.button_01 = QtWidgets.QPushButton("01")
        self.button_02 = QtWidgets.QPushButton("02")
        self.button_03 = QtWidgets.QPushButton("03")
        self.button_04 = QtWidgets.QPushButton("04")
        self.button_05 = QtWidgets.QPushButton("05")
        self.button_06 = QtWidgets.QPushButton("06")
        self.button_07 = QtWidgets.QPushButton("07")
        self.button_08 = QtWidgets.QPushButton("08")
        self.button_09 = QtWidgets.QPushButton("09")
        self.button_10 = QtWidgets.QPushButton("10")
        self.button_11 = QtWidgets.QPushButton("11")
        self.button_12 = QtWidgets.QPushButton("12")
        self.button_13 = QtWidgets.QPushButton("13")
        self.button_14 = QtWidgets.QPushButton("14")
        self.button_15 = QtWidgets.QPushButton("15")
        self.button_16 = QtWidgets.QPushButton("16")
        self.button_17 = QtWidgets.QPushButton("17")
        self.button_18 = QtWidgets.QPushButton("18")
        self.button_19 = QtWidgets.QPushButton("19")
        self.button_20 = QtWidgets.QPushButton("20")
        self.button_21 = QtWidgets.QPushButton("21")
        self.button_22 = QtWidgets.QPushButton("22")
        self.button_23 = QtWidgets.QPushButton("23")
        self.button_24 = QtWidgets.QPushButton("24")
        self.button_25 = QtWidgets.QPushButton("25")
        self.button_26 = QtWidgets.QPushButton("26")
        self.button_27 = QtWidgets.QPushButton("27")
        self.button_28 = QtWidgets.QPushButton("28")
        self.button_29 = QtWidgets.QPushButton("29")

        # self.predefined_layout_grid = QtWidgets.QGridLayout()
        self.predefined_layout_grid = QtWidgets.QGridLayout(self)
        self.predefined_t1_layout_box = QtWidgets.QHBoxLayout(self)
        self.predefined_t2_layout_box = QtWidgets.QHBoxLayout(self)
        self.predefined_t3_layout_box = QtWidgets.QHBoxLayout(self)
        self.predefined_t4_layout_box = QtWidgets.QHBoxLayout(self)
        self.predefined_t5_layout_box = QtWidgets.QHBoxLayout(self)
        self.predefined_t6_layout_box = QtWidgets.QHBoxLayout(self)
        self.predefined_t7_layout_box = QtWidgets.QHBoxLayout(self)
        self.predefined_layout_box = QtWidgets.QHBoxLayout(self)

        # 00 - 04
        self.predefined_t1_layout_box.addWidget(self.button_00)
        self.predefined_t1_layout_box.addWidget(self.button_01)
        self.predefined_t1_layout_box.addWidget(self.button_02)
        self.predefined_t1_layout_box.addWidget(self.button_03)
        self.predefined_t1_layout_box.addWidget(self.button_04)
        # 04 - 09
        self.predefined_t2_layout_box.addWidget(self.button_05)
        self.predefined_t2_layout_box.addWidget(self.button_06)
        self.predefined_t2_layout_box.addWidget(self.button_07)
        self.predefined_t2_layout_box.addWidget(self.button_08)
        self.predefined_t2_layout_box.addWidget(self.button_09)
        # 09 - 14
        self.predefined_t3_layout_box.addWidget(self.button_10)
        self.predefined_t3_layout_box.addWidget(self.button_11)
        self.predefined_t3_layout_box.addWidget(self.button_12)
        self.predefined_t3_layout_box.addWidget(self.button_13)
        self.predefined_t3_layout_box.addWidget(self.button_14)
        # 14 - 19
        self.predefined_t4_layout_box.addWidget(self.button_15)
        self.predefined_t4_layout_box.addWidget(self.button_16)
        self.predefined_t4_layout_box.addWidget(self.button_17)
        self.predefined_t4_layout_box.addWidget(self.button_18)
        self.predefined_t4_layout_box.addWidget(self.button_19)
        # 19 - 24
        self.predefined_t5_layout_box.addWidget(self.button_20)
        self.predefined_t5_layout_box.addWidget(self.button_21)
        self.predefined_t5_layout_box.addWidget(self.button_22)
        self.predefined_t5_layout_box.addWidget(self.button_23)
        self.predefined_t5_layout_box.addWidget(self.button_24)
        # 24 - 29
        self.predefined_t6_layout_box.addWidget(self.button_25)
        self.predefined_t6_layout_box.addWidget(self.button_26)
        self.predefined_t6_layout_box.addWidget(self.button_27)
        self.predefined_t6_layout_box.addWidget(self.button_28)
        self.predefined_t6_layout_box.addWidget(self.button_29)

        self.predefined_layout_grid.addLayout(self.predefined_t1_layout_box, 0, 0)
        self.predefined_layout_grid.addLayout(self.predefined_t2_layout_box, 1, 0)
        self.predefined_layout_grid.addLayout(self.predefined_t3_layout_box, 2, 0)
        self.predefined_layout_grid.addLayout(self.predefined_t4_layout_box, 3, 0)
        self.predefined_layout_grid.addLayout(self.predefined_t5_layout_box, 4, 0)
        self.predefined_layout_grid.addLayout(self.predefined_t6_layout_box, 5, 0)


        self.mover_layout_grid = QtWidgets.QGridLayout(self)
        self.mover_layout_first_box = QtWidgets.QHBoxLayout(self)
        self.mover_layout_second_box = QtWidgets.QHBoxLayout(self)
        self.mover_layout_third_box = QtWidgets.QHBoxLayout(self)

        self.button_move_up = QtWidgets.QPushButton("up")
        self.button_move_down = QtWidgets.QPushButton("down")
        self.button_move_left = QtWidgets.QPushButton("left")
        self.button_move_right = QtWidgets.QPushButton("right")

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
        self.main_layout.addLayout(self.predefined_layout_grid)
        self.main_layout.addWidget(self.mover_label)
        self.main_layout.addLayout(self.mover_layout_grid)
