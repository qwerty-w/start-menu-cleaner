from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core

from main import StartMenuFolder, StartMenu


def wrap_label(label: widgets.QLabel):
    label.setStyleSheet(
        """QLabel
{
    margin-top: 5px;
    margin-left: 3px;
    color: #54595d;
}"""
    )


def wrap_default_checkbox(checkbox: widgets.QCheckBox):
    checkbox.setStyleSheet(
        """QCheckBox
{
    margin-left: 10px;
}"""
    )


def wrap_last_checkbox(checkbox: widgets.QCheckBox):
    checkbox.setStyleSheet(
        """QCheckBox
{
    margin-left: 10px;
    border: 0px solid;
}"""
    )


def get_divider():
    frame = widgets.QFrame()
    # frame.setStyleSheet('QFrame {background: red;}')
    frame.setFrameShape(widgets.QFrame.Shape(4))
    frame.setFrameShadow(widgets.QFrame.Shadow(48))
    frame.setFixedSize(200, 2)
    frame.setStyleSheet('QFrame {margin-left: 7px;}')

    return frame


class MainWindow(widgets.QMainWindow):
    def __init__(self, folders: list[StartMenuFolder]):
        super().__init__()

        self.resize(390, 317)
        self.centralwidget = widgets.QWidget(self)

        self.path2folderLabel = widgets.QLabel(self.centralwidget)
        self.path2folderLabel.setGeometry(core.QRect(280, 20, 111, 16))
        self.path2folderLabel.setStyleSheet('color: grey;')
        # self.path2folderLabel.mousePressEvent()  # todo

        self.move2FolderRadioButton = widgets.QRadioButton(self.centralwidget)
        self.move2FolderRadioButton.setGeometry(core.QRect(280, 40, 91, 17))

        self.deleteRadioButton = widgets.QRadioButton(self.centralwidget)
        self.deleteRadioButton.setGeometry(core.QRect(280, 70, 82, 17))
        self.deleteRadioButton.setChecked(True)  # set default choose

        self.applyButton = widgets.QPushButton(self.centralwidget)
        self.applyButton.setGeometry(core.QRect(290, 270, 81, 31))

        self.scrollArea = widgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(core.QRect(10, 10, 251, 291))
        # self.scrollArea.setMaximumSize(core.QSize(16777215, 291))
        self.scrollArea.setMaximumHeight(291)
        self.scrollArea.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(
            """
            QWidget {background-color: #FFFFFF;}
            QScrollBar {background-color: none;}
            """
        )

        self.scrollAreaWidget = widgets.QWidget()
        # self.scrollAreaWidget.setMinimumWidth(190)
        self.scrollAreaWidgetLayout = widgets.QVBoxLayout()

        for folder in folders:
            folderLabel = widgets.QLabel(self.scrollArea)
            folderLabel.setText(folder.name)
            folderLabel.setStyleSheet("color: #54595d;")
            # folderLabel.mousePressEvent()  # todo

            self.scrollAreaWidgetLayout.addWidget(folderLabel)

            for shortcut in folder.shortcuts:
                shortcutCheckbox = widgets.QCheckBox(self.scrollArea)
                shortcutCheckbox.setText(shortcut.name)
                # todo: add icon
                self.scrollAreaWidgetLayout.addWidget(shortcutCheckbox)

        self.scrollAreaWidgetLayout.addStretch()
        self.scrollAreaWidget.setLayout(self.scrollAreaWidgetLayout)
        self.scrollArea.setWidget(self.scrollAreaWidget)

        self.setCentralWidget(self.centralwidget)

        # self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 396, 21))
        # self.menubar.setObjectName("menubar")
        # MainWindow.setMenuBar(self.menubar)

        self.retranslateUi()
        core.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = core.QCoreApplication.translate
        self.path2folderLabel.setText(_translate('MainWindow', 'C:\\Users\\Downloads'))
        self.move2FolderRadioButton.setText(_translate('MainWindow', 'Move to folder'))
        self.deleteRadioButton.setText(_translate('MainWindow', 'Delete'))
        self.applyButton.setText(_translate('MainWindow', 'Apply'))

        self.setWindowTitle(_translate('MainWindow', 'Start Menu Folders Cleaner'))


def main():
    app = widgets.QApplication([])
    app.setStyleSheet("""
    MainWindow {
        background-color: #EFEFF1;
    }
""")
    window = MainWindow(StartMenu.get_folders())
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
