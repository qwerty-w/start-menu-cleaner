from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui

from main import StartMenuShortcut, StartMenuFolder, StartMenu


def wrapBold(string: str):
    return f'<strong>{string}</strong>'


def wrapU(string: str):
    return f'<u>{string}</u>'


def clearHtmlTags(string: str):
    string = string[string.find('>') + 1:]
    return string[:string.find('<')]


class Widget:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUi()

    def initUi(self):
        ...


class ChooseFolderButton(Widget, widgets.QLabel):
    def __init__(self, *args, **kwargs):
        # self._customToolTipText = None

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setStyleSheet('color: grey;')
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))  # set cursor: pointer

    # def setCustomToolTip(self, text: str):
    #     self._customToolTipText = text

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        path = widgets.QFileDialog.getExistingDirectory(
            self,
            'Choose a folder:',
            options=widgets.QFileDialog.ShowDirsOnly
        )

        if not path:
            return

        metrics = gui.QFontMetrics(self.font())
        text = metrics.elidedText(path, core.Qt.TextElideMode.ElideLeft, self.width())
        self.setText(text)
        self.setToolTip(wrapBold(path))
        # self.setInstantToolTip(wrapBold(path))

    # def enterEvent(self, event: core.QEvent):
    #     if self._customToolTipText:
    #         geometry = self.geometry()
    #         point = self.mapToGlobal(core.QPoint(geometry.x() + geometry.width(), geometry.height()))
    #         core.QTimer.singleShot(
    #             200,
    #             lambda: widgets.QToolTip.showText(point, self._customToolTipText, self)
    #         )
    #
    # def leaveEvent(self, event: gui.QDragLeaveEvent):
    #     if self._customToolTipText:
    #         widgets.QToolTip.hideText()


class MoveToFolderRadioButton(Widget, widgets.QRadioButton):
    pass


class DeleteRadioButton(Widget, widgets.QRadioButton):
    def initUi(self):
        self.setChecked(True)


class ApplyButton(Widget, widgets.QPushButton):
    pass


class StartMenuShortcutGUI(Widget, widgets.QCheckBox):
    def __init__(self, shortcut: StartMenuShortcut, *args, **kwargs):
        self.shortcut = shortcut
        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setText(self.shortcut.name)


class StartMenuFolderGUI(Widget, widgets.QLabel):
    def __init__(self,
                 folder: StartMenuFolder,
                 guiShortcuts: list[StartMenuShortcutGUI],
                 *args,
                 **kwargs):

        self.folder = folder
        self.guiShortcuts = guiShortcuts
        self.disabled = False

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setText(self.folder.name)

    def mousePressEvent(self, event: gui.QMouseEvent):
        if event.button() == 1:
            self.disabled = not self.disabled

            for shortcut in self.guiShortcuts:
                shortcut.setDisabled(self.disabled)


class ShortcutsArea(Widget, widgets.QScrollArea):
    def __init__(self, folders: list[StartMenuFolder], *args, **kwargs):
        self.folders = folders
        self.initWidget = widgets.QWidget()
        self.initLayout = widgets.QVBoxLayout()

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setStyleSheet(
            """
            QWidget {background-color: #FFFFFF;}
            QScrollBar {background-color: none;}
            """
        )
        self.displayShortcuts()

    def addWidget(self, widget: widgets.QWidget):
        self.initLayout.addWidget(widget)

    def showWidgets(self):
        self.initLayout.addStretch()
        self.initWidget.setLayout(self.initLayout)
        self.setWidget(self.initWidget)

    def displayShortcuts(self):
        for folder in self.folders:
            guiFolder = StartMenuFolderGUI(folder, [], self)
            self.addWidget(guiFolder)

            for shortcut in folder.shortcuts:
                guiShortcut = StartMenuShortcutGUI(shortcut, self)
                self.addWidget(guiShortcut)
                guiFolder.guiShortcuts.append(guiShortcut)

        self.showWidgets()


class MainWindow(widgets.QMainWindow):
    def __init__(self, folders: list[StartMenuFolder]):
        super().__init__()

        defaultWindowSize = core.QSize(390, 317)
        self.setFixedSize(defaultWindowSize)

        self.centralwidget = widgets.QWidget(self)

        self.moveOrDeleteGeneralWidget = widgets.QWidget(self.centralwidget)
        self.path2FolderLabel = ChooseFolderButton(self.moveOrDeleteGeneralWidget)
        self.move2FolderRadioButton = MoveToFolderRadioButton(self.moveOrDeleteGeneralWidget)
        self.deleteRadioButton = DeleteRadioButton(self.moveOrDeleteGeneralWidget)
        self.applyButton = ApplyButton(self.centralwidget)
        self.shortcutsArea = ShortcutsArea(folders, self.centralwidget)
        self.setCentralWidget(self.centralwidget)

        # self.menubar = widgets.QMenuBar(self)
        # self.menubar.setGeometry(core.QRect(0, 0, 396, 21))
        # self.setMenuBar(self.menubar)

        self.retranslateUi()
        self.setGeometryUi()
        core.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = core.QCoreApplication.translate

        self.path2FolderLabel.setText(_translate('MainWindow', wrapU('Choose directory')))
        self.move2FolderRadioButton.setText(_translate('MainWindow', 'Move to directory'))
        self.deleteRadioButton.setText(_translate('MainWindow', 'Delete'))
        self.applyButton.setText(_translate('MainWindow', 'Apply'))
        self.setWindowTitle(_translate('MainWindow', 'Start Menu Folders Cleaner'))

    def setGeometryUi(self):
        self.moveOrDeleteGeneralWidget.setGeometry(core.QRect(275, 20, 110, 60))
        self.path2FolderLabel.setGeometry(core.QRect(0, 0, 110, 20))
        self.move2FolderRadioButton.setGeometry(core.QRect(0, 20, 110, 20))
        self.deleteRadioButton.setGeometry(core.QRect(0, 40, 110, 20))
        self.applyButton.setGeometry(core.QRect(285, 270, 80, 31))
        self.shortcutsArea.setGeometry(core.QRect(10, 10, 250, 290))  # -1px h


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
