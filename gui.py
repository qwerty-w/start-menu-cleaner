from typing import Protocol
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui

from main import StartMenuFolder, StartMenuShortcut, StartMenu


class SupportsSetCursor(Protocol):
    def setCursor(self, *args, **kwargs):
        ...


def setCursorPointerOnHover(obj: SupportsSetCursor):
    obj.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))


def wrapBold(string: str):
    return f'<strong>{string}</strong>'


def wrapU(string: str):
    return f'<u>{string}</u>'


def clearHtmlTags(string: str):
    string = string[string.find('>') + 1:]
    return string[:string.find('<')]


class StartMenuShortcutGUI:
    def __init__(self, checkbox: widgets.QCheckBox, shortcut: StartMenuShortcut):
        self.shortcut = shortcut
        self.checkbox = checkbox


class StartMenuFolderGUI:
    def __init__(self, label: widgets.QLabel, folder: StartMenuFolder, guiShortcuts: list[StartMenuShortcutGUI]):
        self.folder = folder
        self.label = label
        self.guiShortcuts = guiShortcuts
        self.disabled = False


class ChooseFolderButton(widgets.QLabel):
    defaultText = core.QCoreApplication.translate('Main Window', 'Choose directory')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(core.QRect(275, 20, 100, 15))
        self.setStyleSheet('color: grey;')
        setCursorPointerOnHover(self)

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        path = widgets.QFileDialog.getExistingDirectory()

        if not path:
            return

        metrics = gui.QFontMetrics(self.font())
        text = metrics.elidedText(path, core.Qt.TextElideMode.ElideRight, self.width())
        self.setText(text)
        self.setToolTip(wrapBold(path))


class MainWindow(widgets.QMainWindow):
    def handleFolderButtonClick(self, folder: StartMenuFolderGUI):
        def handler(event: gui.QMouseEvent):
            for shortcut in folder.guiShortcuts:
                shortcut.checkbox.setDisabled(not folder.disabled)

            folder.disabled = not folder.disabled

        return handler

    def __init__(self, folders: list[StartMenuFolder]):
        super().__init__()

        defaultWindowSize = core.QSize(390, 317)
        self.setFixedSize(defaultWindowSize)

        self.centralwidget = widgets.QWidget(self)

        self.path2FolderLabel = ChooseFolderButton(self.centralwidget)

        self.move2FolderRadioButton = widgets.QRadioButton(self.centralwidget)
        self.move2FolderRadioButton.setGeometry(core.QRect(275, 40, 90, 17))

        self.deleteRadioButton = widgets.QRadioButton(self.centralwidget)
        self.deleteRadioButton.setGeometry(core.QRect(275, 70, 90, 17))
        self.deleteRadioButton.setChecked(True)  # set default choose

        self.applyButton = widgets.QPushButton(self.centralwidget)
        self.applyButton.setGeometry(core.QRect(285, 270, 80, 31))

        self.scrollArea = widgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(core.QRect(10, 10, 250, 290))  # -1px h
        self.scrollArea.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet(
            """
            QWidget {background-color: #FFFFFF;}
            QScrollBar {background-color: none;}
            """
        )

        self.scrollAreaWidget = widgets.QWidget()
        self.scrollAreaWidgetLayout = widgets.QVBoxLayout()

        self.guiFolders = []
        for folder in folders:
            folderLabel = widgets.QLabel(self.scrollArea)
            folderLabel.setText(folder.name)
            folderLabel.setStyleSheet("color: #54595d;")
            self.scrollAreaWidgetLayout.addWidget(folderLabel)

            guiFolder = StartMenuFolderGUI(folderLabel, folder, [])
            self.guiFolders.append(guiFolder)

            guiShortcuts = []
            for shortcut in folder.shortcuts:
                shortcutCheckbox = widgets.QCheckBox(self.scrollArea)
                shortcutCheckbox.setText(shortcut.name)
                # todo: add icon
                self.scrollAreaWidgetLayout.addWidget(shortcutCheckbox)

                guiShortcut = StartMenuShortcutGUI(shortcutCheckbox, shortcut)
                guiShortcuts.append(guiShortcut)

            guiFolder.guiShortcuts = guiShortcuts
            folderLabel.mousePressEvent = self.handleFolderButtonClick(guiFolder)

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

        self.path2FolderLabel.setText(wrapU(self.path2FolderLabel.defaultText))
        self.path2FolderLabel.setToolTip(wrapBold(self.path2FolderLabel.defaultText))

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
