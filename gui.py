import os
import ctypes
from typing import Union
from functools import partial

from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui

from app_text import TEXT
from main import StartMenuShortcut, StartMenuFolder, StartMenuExtendedFolder, StartMenu,\
    DEFAULT_START_MENU_SHORTCUTS_DIRS


def wrapBold(string: str):
    return f'<strong>{string}</strong>'


def wrapU(string: str):
    return f'<u>{string}</u>'


def clearHtmlTags(string: str):
    string = string[string.find('>') + 1:]
    return string[:string.find('<')]


class FilenameValidation:
    specialCharacters = [
        '\\',
        '/',
        ':',
        '*',
        '?',
        '<',
        '>',
        '|'
    ]

    @classmethod
    def validate(cls, name: str):
        return all(map(lambda ch: ch not in name, cls.specialCharacters))


class Widget:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUi()

    def initUi(self):
        ...


class QAction(widgets.QAction):
    def setText(self, text: str) -> None:
        return super().setText(' ' * 4 + text)


class ChooseFolderButton(Widget, widgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setStyleSheet('color: grey;')
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))  # set cursor: pointer

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        path = widgets.QFileDialog.getExistingDirectory(
            self,
            TEXT.SELECT_FOLDER,
            options=widgets.QFileDialog.ShowDirsOnly
        )

        if not path:
            return

        metrics = gui.QFontMetrics(self.font())
        text = metrics.elidedText(path, core.Qt.TextElideMode.ElideLeft, self.width())
        self.setText(text)
        self.setToolTip(wrapBold(path))


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

    def __init__(self, shortcut: StartMenuShortcut, *args, **kwargs):
        self.shortcut = shortcut

        rawPath = core.QFileInfo(self.shortcut.path).symLinkTarget()
        self.targetPath = os.path.normpath(rawPath) if rawPath else None

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setText(self.shortcut.name)
        self.setIcon(self.getIcon())

    def getIcon(self) -> gui.QIcon:
        return self.iconProvider.icon(core.QFileInfo(self.shortcut.path))

    def getTargetIcon(self) -> gui.QIcon:
        fileInfo = core.QFileInfo(self.targetPath if self.targetPath else self.shortcut.path)
        return self.iconProvider.icon(fileInfo)

    def openInExplorer(self):
        os.system(f'explorer.exe /select, "{self.shortcut.path}"')

    def openTargetInExplorer(self):
        os.system(f'explorer.exe /select, "{self.targetPath}"')

    def contextMenuEvent(self, event: gui.QContextMenuEvent):
        menu = widgets.QMenu()
        menu.setStyleSheet('QMenu { color: black; background-color: white; }'
                           'QMenu::item:selected { color: black; background-color: #F0F0F0; }')

        openInExplorerAction = QAction(self)
        openInExplorerAction.setText(TEXT.OPEN_SHORTCUT_PATH)
        openTargetInExplorerAction = QAction(self)
        openTargetInExplorerAction.setText(TEXT.OPEN_TARGET_PATH)

        menu.addActions([openInExplorerAction, openTargetInExplorerAction])
        action = menu.exec(event.globalPos())

        if action is openInExplorerAction:
            self.openInExplorer()

        elif action is openTargetInExplorerAction:
            self.openTargetInExplorer()


class StartMenuFolderGUI(Widget, widgets.QLabel):
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
        self.isSkipped = False

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setText(self.folder.name)
        self.setStyleSheet(self.notKeptStyleSheet)

    def contextMenuEvent(self, event: gui.QContextMenuEvent) -> None:
        menu = widgets.QMenu(self)
        menu.setStyleSheet('QMenu { color: black; background-color: white; }'
                           'QMenu::item:selected { color: black; background-color: #F0F0F0; }')

        if not self.isSkipped:
            keepAction = QAction(self)
            keepAction.setText(TEXT.UNKEEP_FOLDER if self.isKept else TEXT.KEEP_FOLDER)

        else:
            keepAction = None

        skipAction = QAction(self)
        skipAction.setText(TEXT.DONT_SKIP_FOLDER if self.isSkipped else TEXT.SKIP_FOLDER)

        menu.addActions([act for act in [keepAction, skipAction] if act is not None])
        action = menu.exec(event.globalPos())

        if not action:
            return

        elif action is keepAction:
            self.reverseKeptState()

        elif action is skipAction:
            self.reverseSkippedState()

    def reverseKeptState(self):
        self.isKept = not self.isKept

        if self.isKept:
            self.setStyleSheet(self.keptStyleSheet)

        else:
            self.setStyleSheet(self.notKeptStyleSheet)

    def reverseSkippedState(self):
        self.isSkipped = not self.isSkipped

        for shortcut in self.guiShortcuts:
            shortcut.setDisabled(self.isSkipped)

        if self.isKept:
            self.reverseKeptState()

    def mousePressEvent(self, event: gui.QMouseEvent):
        if event.button() == 1 and not self.isSkipped:
            self.reverseKeptState()


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

    def updateShortcuts(self):
        self.folders = StartMenu.get_folders()
        self.initWidget = widgets.QWidget()
        self.initLayout = widgets.QVBoxLayout()
        self.displayShortcuts()


class ApplyToQuestionLabel(Widget, widgets.QLabel):
    pass


class ApplyToCheckedRadioButton(Widget, widgets.QRadioButton):
    pass


class ApplyToUncheckedRadioButton(Widget, widgets.QRadioButton):
    def initUi(self):
        self.setChecked(True)


class ForAllUsersNewShortcutDialogCheckbox(Widget, widgets.QCheckBox):
    def initUi(self):
        self.setText(TEXT.FOR_ALL_USERS)


class NewShortcutNameInputDialog(Widget, widgets.QInputDialog):
    def __init__(self, *args, **kwargs):
        self._fixedSize = None

        super().__init__(*args, **kwargs)

        self.forAllUsersCheckbox = ForAllUsersNewShortcutDialogCheckbox(self)
        self.setGeometryUi()

    def initUi(self):
        self.setInputMode(widgets.QInputDialog.TextInput)
        self.setWindowFlag(core.Qt.WindowContextHelpButtonHint, False)
        self.setModal(True)
        self.setLabelText(TEXT.ENTER_NAME)
        self.setWindowTitle(TEXT.NEW_SHORTCUT)
        self.setFixedSize(core.QSize(300, 90))

    def setGeometryUi(self):
        self.forAllUsersCheckbox.setGeometry(210, 10, 120, 13)

    def setFixedSize(self, a0: core.QSize) -> None:
        self._fixedSize = a0

        if self._fixedSize.height() == 90:
            self._fixedSize.setHeight(91)

    def resizeEvent(self, event: gui.QResizeEvent) -> None:
        """
        NOTICE: Overriding this method and self.setFixedSize needed because default
                QInputDialog.setFixedSize does not work. It only changes width and
                does not set fixed size, window remain resizable (I think because
                self.exec() call self.setFixedSize(defaultQSize))
        """
        if self._fixedSize is not None and event.size() != self._fixedSize:
            super().setFixedSize(self._fixedSize)


class AddNewShortcutButton(Widget, widgets.QPushButton):
    def __init__(self, mainWindow: widgets.QMainWindow, *args, **kwargs):
        self.mainWindow = mainWindow
        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setIcon(gui.QIcon(r'icons\wmploc_474.ico'))
        self.setStyleSheet("""
        QPushButton {
            color: #ffffff;
            background-color: #EFEFF1; 
            border: none;
        }""")
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        if event.button() != 1:
            return

        targetPath = widgets.QFileDialog.getOpenFileName(
            self,
            TEXT.SELECT_FILE,
        )[0]
        if not targetPath:
            return

        dialog = NewShortcutNameInputDialog()
        defaultCriticalBox = partial(
            widgets.QMessageBox.critical,
            dialog,
            TEXT.ERROR,
            buttons=widgets.QMessageBox.StandardButton.Ok
        )

        fileInfo = core.QFileInfo(targetPath)
        iconProvider = widgets.QFileIconProvider()
        dialog.setWindowIcon(iconProvider.icon(fileInfo))

        code, name = dialog.exec(), dialog.textValue()
        systemDir, userDir = DEFAULT_START_MENU_SHORTCUTS_DIRS

        if not code:
            return

        if not name:
            defaultCriticalBox(TEXT.NAME_CANT_BE_EMPTY)
            return

        if not FilenameValidation.validate(name):
            defaultCriticalBox(
                TEXT.CHARACTERS_CANT_BE_USED.format(
                    characters=" ".join(FilenameValidation.specialCharacters)
                )
            )
            return

        if dialog.forAllUsersCheckbox.isChecked() and not ctypes.windll.shell32.IsUserAnAdmin():
            defaultCriticalBox(TEXT.NEED_ADMIN_PRIVILEGES)
            return

        shortcutDir = systemDir if dialog.forAllUsersCheckbox.isChecked() else userDir
        core.QFile(targetPath).link(os.path.join(shortcutDir, name + '.lnk'))
        widgets.QMessageBox.information(
            dialog,
            TEXT.COMPLETE,
            TEXT.SHORTCUT_CREATED,
            widgets.QMessageBox.StandardButton.Ok
        )
        # self.mainWindow.shortcutsArea.updateShortcuts()  # make no sense, shortcut creating outside of folder

def popEmptyFolders(folders: list[Union[StartMenuFolder, StartMenuExtendedFolder]]):
    return [folders.pop(index) for index, folder in enumerate(folders) if folder.is_empty()]


class MainWindow(widgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.folders = StartMenu.get_folders()
        self.emptyFolders = popEmptyFolders(self.folders)
        self.centralwidget = widgets.QWidget(self)

        self.addNewShortcutButton = AddNewShortcutButton(self, self.centralwidget)

        self.moveOrDeleteGeneralWidget = widgets.QWidget(self.centralwidget)
        self.path2FolderLabel = ChooseFolderButton(self.moveOrDeleteGeneralWidget)
        self.move2FolderRadioButton = MoveToFolderRadioButton(self.moveOrDeleteGeneralWidget)
        self.deleteRadioButton = DeleteRadioButton(self.moveOrDeleteGeneralWidget)

        self.apply2QuestionGeneralWidget = widgets.QWidget(self.centralwidget)
        self.apply2Question = ApplyToQuestionLabel(self.apply2QuestionGeneralWidget)
        self.apply2Checked = ApplyToCheckedRadioButton(self.apply2QuestionGeneralWidget)
        self.apply2Unchecked = ApplyToUncheckedRadioButton(self.apply2QuestionGeneralWidget)

        self.apply2EmptyFolders = ApplyToEmptyFoldersButton(self.emptyFolders, self.centralwidget)

        self.applyButton = ApplyButton(self.centralwidget)
        self.shortcutsArea = ShortcutsArea(self.folders, self.centralwidget)

        self.setFixedSize(core.QSize(390, 317))
        self.setStyleSheet('MainWindow { background-color: #EFEFF1; }')
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi()
        self.setGeometryUi()
        core.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = core.QCoreApplication.translate

        self.path2FolderLabel.setText(wrapU(TEXT.SELECT_DIRECTORY))
        self.move2FolderRadioButton.setText(TEXT.MOVE_TO_DIRECTORY)
        self.deleteRadioButton.setText(TEXT.DELETE)
        self.apply2Question.setText(TEXT.APPLY_TO)
        self.apply2Checked.setText(TEXT.SELECTED)
        self.apply2Unchecked.setText(TEXT.UNSELECTED)
        self.apply2EmptyFolders.setText(TEXT.APPLY_TO_EMPTY_FOLDERS)
        self.applyButton.setText(TEXT.APPLY)
        self.setWindowTitle(TEXT.WINDOW_TITLE)

    def setGeometryUi(self):
        self.addNewShortcutButton.setGeometry(10, 5, 16, 16)

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
        self.shortcutsArea.setGeometry(core.QRect(10, 25, 250, 275))  # -1px h


def main():
    app = widgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
