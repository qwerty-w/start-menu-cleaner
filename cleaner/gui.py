import os
import subprocess
from functools import partial

from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui

from . import log
from .app_text import TEXT
from .menu import StartMenuShortcut, SMFolder, StartMenu
from .utils import resource_path, HTML, validate_filename, FILENAME_FORBIDDEN_CHARACTERS


LOG = log.getLogger(__name__)


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

        path = os.path.normpath(path)
        metrics = gui.QFontMetrics(self.font())
        text = metrics.elidedText(path, core.Qt.TextElideMode.ElideLeft, self.width())
        self.setText(text)
        self.setToolTip(HTML(path).wrap_bold())


class MoveToFolderRadioButton(Widget, widgets.QRadioButton):
    pass


class RemoveRadioButton(Widget, widgets.QRadioButton):
    def initUi(self):
        self.setChecked(True)


class ApplyToEmptyFoldersButton(Widget, widgets.QCheckBox):
    def __init__(self, emptyFolders: list[SMFolder], *args, **kwargs):
        self.emptyFolders = emptyFolders

        super().__init__(*args, **kwargs)

    def initUi(self):
        tip = TEXT.NO_EMPTY_FOLDERS if not self.emptyFolders else ', '.join(f'"{x.name}"' for x in self.emptyFolders)
        self.setToolTip(tip)


class ApplyButton(Widget, widgets.QPushButton):
    def __init__(self, mainWindow: 'MainWindow', *args, **kwargs):
        self.mainWindow = mainWindow

        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        if event.button() != 1:
            return

        foldersToClean: list[StartMenu.folder_to_clean] = []
        for guiFolder in self.mainWindow.shortcutsArea.guiFolders:
            if guiFolder.isSkipped:
                continue

            folderToClean = StartMenu.folder_to_clean(guiFolder.folder, guiFolder.isKept, [], [])
            apply2Checked = self.mainWindow.apply2Checked.isChecked()

            for guiShortcut in guiFolder.guiShortcuts:
                if apply2Checked is guiShortcut.isChecked():
                    folderToClean.shortcuts_to_apply.append(guiShortcut.shortcut)
                else:
                    folderToClean.shortcuts_to_save.append(guiShortcut.shortcut)

            if not folderToClean.shortcuts_to_apply and folderToClean.is_kept:
                continue

            foldersToClean.append(folderToClean)

        if self.mainWindow.apply2EmptyFolders.isChecked():
            foldersToClean.extend(
                StartMenu.folder_to_clean(f, False, [], []) for f in self.mainWindow.apply2EmptyFolders.emptyFolders
            )

        if self.mainWindow.move2FolderRadioButton.isChecked():
            path = HTML(self.mainWindow.path2FolderLabel.toolTip()).clear()

            if not path:
                widgets.QMessageBox.critical(
                    self.parent(),
                    TEXT.ERROR,
                    TEXT.NEED_SELECT_DIRECTORY,
                    widgets.QMessageBox.StandardButton.Ok
                )
                return

            action = StartMenu.clean_action.move(path)
            actionText = TEXT.MOVED
        else:
            action = StartMenu.clean_action.remove()
            actionText = TEXT.REMOVED

        cleanResult = StartMenu.clean(action, foldersToClean)
        if cleanResult.errors:
            widgets.QMessageBox.warning(
                self.parent(),
                TEXT.WARNING,
                TEXT.HAVE_CLEAN_ERRORS_WARNING.format(
                    errors_count=len(cleanResult.errors),
                    log_fp=cleanResult.log_fp,
                    cleanedFolders=cleanResult.cleaned_folders,
                    appliedShortcuts=cleanResult.applied_shortcuts,
                    actionText=actionText
                ),
                widgets.QMessageBox.StandardButton.Ok
            )
        else:
            widgets.QMessageBox.information(
                self.parent(),
                TEXT.COMPLETE,
                TEXT.APPLY_CLEANED.format(
                    cleanedFolders=cleanResult.cleaned_folders,
                    appliedShortcuts=cleanResult.applied_shortcuts,
                    actionText=actionText
                ),
                widgets.QMessageBox.StandardButton.Ok
            )

        update_window(self.mainWindow)


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
        subprocess.Popen(f'explorer.exe /select, "{self.shortcut.path}"', shell=True)

    def openTargetInExplorer(self):
        subprocess.Popen(f'explorer.exe /select, "{self.targetPath}"', shell=True)

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
                 folder: SMFolder,
                 guiShortcuts: list[StartMenuShortcutGUI],
                 area: 'ShortcutsArea',
                 *args,
                 **kwargs):

        self.folder = folder
        self.guiShortcuts = guiShortcuts
        self.area = area

        self.isKept = None
        self.keptStyleSheet = 'color: #228BE6;'
        self.notKeptStyleSheet = 'color: #54595d;'

        self.isSkipped = None
        self.isKeptBeforeSkipping = None

        super().__init__(area, *args, **kwargs)

    def initUi(self):
        self.setText(self.folder.name)
        self.setKeptState(True)
        self.setSkippedState(False)

    def setKeptState(self, value: bool):
        self.isKept = value
        self.setStyleSheet(self.keptStyleSheet if value else self.notKeptStyleSheet)

    def setSkippedState(self, value: bool):
        self.isSkipped = value

        for shortcut in self.guiShortcuts:
            if value:
                shortcut.setChecked(False)
            shortcut.setDisabled(value)

        if value and self.isKept:
            self.reverseKeptState()
            self.isKeptBeforeSkipping = True

        elif not value and self.isKeptBeforeSkipping:
            self.reverseKeptState()
            self.isKeptBeforeSkipping = None

    def reverseKeptState(self):
        self.setKeptState(not self.isKept)

    def reverseSkippedState(self):
        self.setSkippedState(not self.isSkipped)

    def contextMenuEvent(self, event: gui.QContextMenuEvent) -> None:
        menu = widgets.QMenu(self)
        menu.setStyleSheet('QMenu { color: black; background-color: white; }'
                           'QMenu::item:selected { color: black; background-color: #F0F0F0; }')

        keepAction = QAction(self)
        keepAction.setText(TEXT.UNKEEP_FOLDER if self.isKept else TEXT.KEEP_FOLDER)

        keepAllFoldersAction = QAction(self)
        allFoldersIsKept = self.area.allFoldersIsKept()
        keepAllFoldersAction.setText(TEXT.UNKEEP_ALL_FOLDERS if allFoldersIsKept else TEXT.KEEP_ALL_FOLDERS)

        skipAction = QAction(self)
        skipAction.setText(TEXT.DONT_SKIP_FOLDER if self.isSkipped else TEXT.SKIP_FOLDER)

        actions = [
            keepAction,
            keepAllFoldersAction,
            skipAction
        ] if not self.isSkipped else [skipAction]

        menu.addActions(actions)
        action = menu.exec(event.globalPos())

        if not action:
            return

        elif action is keepAction:
            self.reverseKeptState()

        elif action is skipAction:
            self.reverseSkippedState()

        elif action is keepAllFoldersAction:
            keptState = not allFoldersIsKept

            for folder in self.area.guiFolders:
                if folder.isKept is not keptState and not folder.isSkipped:
                    folder.setKeptState(keptState)

    def mousePressEvent(self, event: gui.QMouseEvent):
        if event.button() == 1 and not self.isSkipped:
            self.reverseKeptState()


class ShortcutsArea(Widget, widgets.QScrollArea):
    def __init__(self, folders: list[SMFolder], *args, **kwargs):
        self.folders = folders
        self.guiFolders: list[StartMenuFolderGUI] = []

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
            QScrollBar::handle:horizontal {background-color: #228BE6}
            QScrollArea {background-color: #F0F0F0; border: 1px solid #228BE6;}
            """
        )
        self.displayShortcuts()

    def allFoldersIsKept(self) -> bool:
        return all(folder.isKept for folder in self.guiFolders if not folder.isSkipped)

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

            self.guiFolders.append(guiFolder)

        self.showWidgets()


class ApplyToQuestionLabel(Widget, widgets.QLabel):
    def initUi(self):
        self.setStyleSheet('color: #54595d;')


class ApplyToCheckedRadioButton(Widget, widgets.QRadioButton):
    def initUi(self):
        self.setChecked(True)


class ApplyToUncheckedRadioButton(Widget, widgets.QRadioButton):
    pass


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
    def initUi(self):
        self.setIcon(gui.QIcon(resource_path(r'icons\icons8-plus-math-50.png')))
        self.setStyleSheet("""
        QPushButton {
            color: #ffffff;
            background-color: #EFEFF1; 
            border: none;
        }""")
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))
        self.setToolTip(TEXT.ADD_NEW_SHORTCUT_TOOL_TIP)

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
        systemDir, userDir = StartMenu.default_dirs.system, StartMenu.default_dirs.user

        if not code:
            return

        if not name:
            defaultCriticalBox(TEXT.NAME_CANT_BE_EMPTY)
            return

        if not validate_filename(name):
            defaultCriticalBox(
                TEXT.CHARACTERS_CANT_BE_USED.format(
                    characters=" ".join(FILENAME_FORBIDDEN_CHARACTERS)
                )
            )
            return

        if dialog.forAllUsersCheckbox.isChecked() and not systemDir.is_accessible:
            defaultCriticalBox(TEXT.NEED_ADMIN_RIGHTS_FOR_CREATE_ALL_USERS_SHORTCUT)
            return

        shortcutDir = systemDir if dialog.forAllUsersCheckbox.isChecked() else userDir
        core.QFile(targetPath).link(os.path.join(shortcutDir, name + '.lnk'))
        LOG.info(f'Add new shortcut "{name}" in "{shortcutDir}"')
        widgets.QMessageBox.information(
            dialog,
            TEXT.COMPLETE,
            TEXT.SHORTCUT_CREATED,
            widgets.QMessageBox.StandardButton.Ok
        )


class RefreshWindowButton(Widget, widgets.QPushButton):
    def __init__(self, mainWindow: 'MainWindow', *args, **kwargs):
        self.mainWindow = mainWindow
        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setIcon(gui.QIcon(resource_path(r'icons\icons8-synchronize-50.png')))
        self.setStyleSheet("""
        QPushButton {
            color: #ffffff;
            background-color: #EFEFF1; 
            border: none;
        }""")
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))
        self.setToolTip(TEXT.REFRESH_WINDOW_TOOL_TIP)

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        if event.button() != 1:
            return

        update_window(self.mainWindow)


def popEmptyFolders(folders: list[SMFolder]):
    e = []
    index = 0

    while index < len(folders):
        if folders[index].is_empty():
            e.append(folders.pop(index))
            continue

        index += 1

    return e


class MainWindow(widgets.QMainWindow):
    def __init__(self):
        super().__init__()

        folders = StartMenu.get_folders()
        emptyFolders = popEmptyFolders(folders)
        self.centralwidget = widgets.QWidget(self)

        self.addNewShortcutButton = AddNewShortcutButton(self.centralwidget)
        self.refreshWindowButton = RefreshWindowButton(self, self.centralwidget)

        self.moveOrRemoveGeneralWidget = widgets.QWidget(self.centralwidget)
        self.path2FolderLabel = ChooseFolderButton(self.moveOrRemoveGeneralWidget)
        self.move2FolderRadioButton = MoveToFolderRadioButton(self.moveOrRemoveGeneralWidget)
        self.removeRadioButton = RemoveRadioButton(self.moveOrRemoveGeneralWidget)

        self.apply2QuestionGeneralWidget = widgets.QWidget(self.centralwidget)
        self.apply2Question = ApplyToQuestionLabel(self.apply2QuestionGeneralWidget)
        self.apply2Checked = ApplyToCheckedRadioButton(self.apply2QuestionGeneralWidget)
        self.apply2Unchecked = ApplyToUncheckedRadioButton(self.apply2QuestionGeneralWidget)

        self.apply2EmptyFolders = ApplyToEmptyFoldersButton(emptyFolders, self.centralwidget)

        self.applyButton = ApplyButton(self, self.centralwidget)
        self.shortcutsArea = ShortcutsArea(folders, self.centralwidget)

        self.setFixedSize(core.QSize(390, 317))
        self.setStyleSheet('MainWindow { background-color: #EFEFF1; }')
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi()
        self.setGeometryUi()
        self.setWindowIcon(gui.QIcon(resource_path('icons/menu.png')))
        core.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = core.QCoreApplication.translate

        self.path2FolderLabel.setText(HTML(TEXT.SELECT_DIRECTORY).wrap_underline())
        self.move2FolderRadioButton.setText(TEXT.MOVE_TO_DIRECTORY)
        self.removeRadioButton.setText(TEXT.REMOVE)
        self.apply2Question.setText(TEXT.APPLY_TO)
        self.apply2Checked.setText(TEXT.SELECTED)
        self.apply2Unchecked.setText(TEXT.UNSELECTED)
        self.apply2EmptyFolders.setText(TEXT.APPLY_TO_EMPTY_FOLDERS)
        self.applyButton.setText(TEXT.APPLY)
        self.setWindowTitle(TEXT.WINDOW_TITLE)

    def setGeometryUi(self):
        self.addNewShortcutButton.setGeometry(10, 5, 16, 16)
        self.refreshWindowButton.setGeometry(32, 5, 16, 16)

        self.moveOrRemoveGeneralWidget.setGeometry(core.QRect(275, 20, 110, 60))
        self.path2FolderLabel.setGeometry(core.QRect(0, 0, 110, 20))
        self.move2FolderRadioButton.setGeometry(core.QRect(0, 20, 110, 20))
        self.removeRadioButton.setGeometry(core.QRect(0, 40, 110, 20))

        self.apply2QuestionGeneralWidget.setGeometry(core.QRect(275, 85, 110, 60))
        self.apply2Question.setGeometry(core.QRect(0, 0, 110, 20))
        self.apply2Checked.setGeometry(core.QRect(0, 20, 110, 20))
        self.apply2Unchecked.setGeometry(core.QRect(0, 40, 110, 20))

        self.apply2EmptyFolders.setGeometry(core.QRect(275, 150, 110, 30))
        self.applyButton.setGeometry(core.QRect(285, 270, 80, 31))
        self.shortcutsArea.setGeometry(core.QRect(10, 25, 250, 275))  # -1px h


def update_window(current_window: MainWindow):
    LOG.info('Update window')
    current_window.close()

    StartMenu.update()
    w = MainWindow()
    w.show()
    return w


def warn_inaccessible_dirs(warning_parent: widgets.QWidget) -> None:
    i_dirs = [d for d in StartMenu.default_dirs if not d.is_accessible]

    if not i_dirs:
        return

    LOG.info('Show warning about inaccessible SM dirs')

    for d in i_dirs:
        if d is StartMenu.default_dirs.system:
            widgets.QMessageBox.warning(
                warning_parent,
                TEXT.NO_ACCESS_WARNING,
                TEXT.NEED_ADMIN_RIGHTS_FOR_ALL_USERS_SM_PATH.format(sys_d=StartMenu.default_dirs.system.path),
                widgets.QMessageBox.StandardButton.Ok
            )
            break

    else:
        text = TEXT.NO_ACCESS_TO_DIRS if len(i_dirs) > 1 else TEXT.NO_ACCESS_TO_DIR
        widgets.QMessageBox.warning(
            warning_parent,
            TEXT.NO_ACCESS_WARNING,
            text.format(dirs='\n'.join(d.path for d in i_dirs)),
            widgets.QMessageBox.StandardButton.Ok
        )
