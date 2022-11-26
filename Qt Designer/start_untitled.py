import untitled
from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QMainWindow, untitled.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
