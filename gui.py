import os
from typing import Union
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui

from main import StartMenuShortcut, StartMenuFolder, StartMenuExtendedFolder, StartMenu


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


class ApplyToEmptyFoldersButton(Widget, widgets.QCheckBox):
    def __init__(self, emptyFolders: list[Union[StartMenuFolder, StartMenuExtendedFolder]], *args, **kwargs):
        self.emptyFolders = emptyFolders

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setChecked(True)
        self.setToolTip(', '.join(f'"{x.name}"' for x in self.emptyFolders))


class ApplyButton(Widget, widgets.QPushButton):
    pass


class StartMenuShortcutGUI(Widget, widgets.QCheckBox):
    iconProvider = widgets.QFileIconProvider()

    class ContextMenu(Widget, widgets.QMenu):
        actionsTexts = {
            'open-shortcut-path': '',
            'open-target-path': ''
        }

        def initUi(self):
            for text in self.actionsTexts.values():
                self.addAction(widgets.QAction(text, self))
            self.setStyleSheet('QMenu { color: black; background-color: white; }'
                               'QMenu::item:selected { color: black; background-color: #F0F0F0; }')

        def handleAction(self, action: widgets.QAction, parent: 'StartMenuShortcutGUI'):
            index = self.actions().index(action)

            if index == 0:
                os.system(f'explorer.exe /select, "{parent.shortcut.path}"')

            elif index == 1:
                rawPath = core.QFileInfo(parent.shortcut.path).symLinkTarget()
                targetPath = os.path.normpath(rawPath) if rawPath else parent.shortcut.path
                os.system(f'explorer.exe /select, "{targetPath}"')

    def __init__(self, shortcut: StartMenuShortcut, *args, **kwargs):
        self.shortcut = shortcut
        self.unavailableIcon = gui.QIcon(r'icons\unavailable.png')  # todo: maybe remove

        super().__init__(*args, **kwargs)

    def getIcon(self) -> gui.QIcon:
        return self.iconProvider.icon(core.QFileInfo(self.shortcut.path))

    def getTargetIcon(self) -> gui.QIcon:
        shortcutInfo = core.QFileInfo(self.shortcut.path)
        target = shortcutInfo.symLinkTarget()
        fileInfo = core.QFileInfo(target) if target else shortcutInfo
        return self.iconProvider.icon(fileInfo)

    def initUi(self):
        self.setText(self.shortcut.name)
        self.setIcon(self.getIcon())

    def contextMenuEvent(self, event: gui.QContextMenuEvent):
        menu = self.ContextMenu()
        action = menu.exec(event.globalPos())

        if action:
            menu.handleAction(action, self)


class StartMenuFolderGUI(Widget, widgets.QLabel):
    class ContextMenu(Widget, widgets.QMenu):
        actionsTexts = {
            'keep-action': {
                'keep': '',
                'unkeep': ''
            },
            'skip-action': {
                'skip': '',
                'dont-skip': ''
            }
        }

        def initUi(self):
            parent = self.parent()
            keepActionText = self.actionsTexts['keep-action']['unkeep' if parent.isKept else 'keep']
            skipActionText = self.actionsTexts['skip-action']['dont-skip' if parent.disabledShortcuts else 'skip']
            self.addActions(widgets.QAction(' ' * 4 + text, self) for text in [keepActionText, skipActionText])

            self.setStyleSheet('QMenu { color: black; background-color: white; }'
                               'QMenu::item:selected { color: black; background-color: #F0F0F0; }')

        def handleAction(self, action: widgets.QAction, parent: 'StartMenuFolderGUI'):
            index = self.actions().index(action)

            if index == 0:
                parent.setKeptReverse()

            elif index == 1:
                parent.disabledShortcuts = not parent.disabledShortcuts
                for shortcut in parent.guiShortcuts:
                    shortcut.setDisabled(parent.disabledShortcuts)

    def __init__(self,
                 folder: Union[StartMenuFolder, StartMenuExtendedFolder],
                 guiShortcuts: list[StartMenuShortcutGUI],
                 *args,
                 **kwargs):

        self.folder = folder
        self.guiShortcuts = guiShortcuts
        self.isKept = False
        self.keptStyleSheet = 'color: green;'
        self.notKeptStyleSheet = 'color: #54595d;'
        self.disabledShortcuts = False

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setText(self.folder.name)
        self.setStyleSheet(self.notKeptStyleSheet)

    def contextMenuEvent(self, event: gui.QContextMenuEvent) -> None:
        menu = self.ContextMenu(self)
        action = menu.exec(event.globalPos())

        if action:
            menu.handleAction(action, self)

    def setKeptReverse(self):
        self.isKept = not self.isKept

        if self.isKept:
            self.setStyleSheet(self.keptStyleSheet)

        else:
            self.setStyleSheet(self.notKeptStyleSheet)

    def mousePressEvent(self, event: gui.QMouseEvent):
        if event.button() == 1:
            self.setKeptReverse()


class ShortcutsArea(Widget, widgets.QScrollArea):
    def __init__(self, folders: list[Union[StartMenuFolder, StartMenuExtendedFolder]], *args, **kwargs):
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


class ApplyToQuestionLabel(Widget, widgets.QLabel):
    pass


class ApplyToCheckedRadioButton(Widget, widgets.QRadioButton):
    pass


class ApplyToUncheckedRadioButton(Widget, widgets.QRadioButton):
    def initUi(self):
        self.setChecked(True)


def pop_empty_folders(folders: list[Union[StartMenuFolder, StartMenuExtendedFolder]]):
    return [folders.pop(index) for index, folder in enumerate(folders) if folder.is_empty()]


class MainWindow(widgets.QMainWindow):
    def __init__(self, folders: list[Union[StartMenuFolder, StartMenuExtendedFolder]]):
        super().__init__()
        emptyFolders = pop_empty_folders(folders)

        defaultWindowSize = core.QSize(390, 317)
        self.setFixedSize(defaultWindowSize)

        self.centralwidget = widgets.QWidget(self)

        self.moveOrDeleteGeneralWidget = widgets.QWidget(self.centralwidget)
        self.path2FolderLabel = ChooseFolderButton(self.moveOrDeleteGeneralWidget)
        self.move2FolderRadioButton = MoveToFolderRadioButton(self.moveOrDeleteGeneralWidget)
        self.deleteRadioButton = DeleteRadioButton(self.moveOrDeleteGeneralWidget)

        self.apply2QuestionGeneralWidget = widgets.QWidget(self.centralwidget)
        self.apply2Question = ApplyToQuestionLabel(self.apply2QuestionGeneralWidget)
        self.apply2Checked = ApplyToCheckedRadioButton(self.apply2QuestionGeneralWidget)
        self.apply2Unchecked = ApplyToUncheckedRadioButton(self.apply2QuestionGeneralWidget)

        self.apply2EmptyFolders = ApplyToEmptyFoldersButton(emptyFolders, self.centralwidget)

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
        self.apply2Question.setText(_translate('MainWindow', 'Apply to:'))
        self.apply2Checked.setText(_translate('MainWindow', 'Selected'))
        self.apply2Unchecked.setText(_translate('MainWindow', 'Unselected'))
        self.apply2EmptyFolders.setText(_translate('MainWindow', 'Apply to empty\nfolders'))
        self.applyButton.setText(_translate('MainWindow', 'Apply'))
        self.setWindowTitle(_translate('MainWindow', 'Start Menu Folders Cleaner'))
        StartMenuShortcutGUI.ContextMenu.actionsTexts['open-shortcut-path'] = 'Open shortcut path'
        StartMenuShortcutGUI.ContextMenu.actionsTexts['open-target-path'] = 'Open target path'
        StartMenuFolderGUI.ContextMenu.actionsTexts['keep-action'] = {
            'keep': _translate('MainWindow', 'Keep folder'),
            'unkeep': _translate('MainWindow', 'Unkeep folder')
        }
        StartMenuFolderGUI.ContextMenu.actionsTexts['skip-action'] = {
            'skip': _translate('MainWindow', 'Skip folder completely'),
            'dont-skip': _translate('MainWindow', 'Don\'t skip folder')
        }

    def setGeometryUi(self):
        self.moveOrDeleteGeneralWidget.setGeometry(core.QRect(275, 20, 110, 60))
        self.path2FolderLabel.setGeometry(core.QRect(0, 0, 110, 20))
        self.move2FolderRadioButton.setGeometry(core.QRect(0, 20, 110, 20))
        self.deleteRadioButton.setGeometry(core.QRect(0, 40, 110, 20))

        self.apply2QuestionGeneralWidget.setGeometry(core.QRect(275, 85, 110, 60))
        self.apply2Question.setGeometry(core.QRect(0, 0, 110, 20))
        self.apply2Checked.setGeometry(core.QRect(0, 20, 110, 20))
        self.apply2Unchecked.setGeometry(core.QRect(0, 40, 110, 20))

        self.apply2EmptyFolders.setGeometry(core.QRect(275, 150, 110, 30))
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
