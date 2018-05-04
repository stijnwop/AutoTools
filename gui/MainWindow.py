from Qt import QtCore, QtGui, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.curFile = ''

        self.textEdit = QtWidgets.QTextEdit()
        self.setCentralWidget(self.textEdit)
