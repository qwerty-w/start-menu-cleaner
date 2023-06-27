import os
import subprocess
from typing import Optional

from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui

from . import log
from .app_text import TEXT
from .menu import StartMenuShortcut, SMFolder, StartMenu
from .utils import resource_path, HTML, validate_filename, FILENAME_FORBIDDEN_CHARACTERS


LOG = log.getLogger(__name__)


def popEmptyFolders(folders: list[SMFolder]) -> list[SMFolder]:
    e, index = [], 0

    while index < len(folders):
        if folders[index].is_empty():
            e.append(folders.pop(index))
            continue

        index += 1

    return e


def load_fonts(ret_font: str = None, ret_size: int = 9) -> Optional[gui.QFont]:
    for fn in os.listdir(resource_path('fonts')):
        gui.QFontDatabase.addApplicationFont(resource_path(f'fonts/{fn}'))

    if ret_font:
        return gui.QFont(ret_font, ret_size)


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
                TEXT.NEED_ADMIN_RIGHTS_FOR_ALL_USERS_SM_PATH.format(sys_d=StartMenu.default_dirs.system.path)
            )
            break

    else:
        text = TEXT.NO_ACCESS_TO_DIRS if len(i_dirs) > 1 else TEXT.NO_ACCESS_TO_DIR
        widgets.QMessageBox.warning(
            warning_parent,
            TEXT.NO_ACCESS_WARNING,
            text.format(dirs='\n'.join(d.path for d in i_dirs))
        )


def update_window(current_window: 'MainWindow') -> 'MainWindow':
    LOG.info('Update window')
    current_window.close()

    StartMenu.update()
    w = MainWindow()
    w.show()
    return w


def defaultCriticalBox(text: str, parent: widgets.QWidget = None, title: str = TEXT.ERROR) -> None:
    widgets.QMessageBox.critical(parent, title, text, widgets.QMessageBox.StandardButton.Ok)


class Widget:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUi()

    def initUi(self):
        ...


class EnterShortcutNameDialog(Widget, widgets.QInputDialog):
    MAX_TEXT_VALUE_LENGTH = 200

    def __init__(self, title: str, text: str, parent: widgets.QWidget = None, *, icon: gui.QIcon = None):
        self._size = core.QSize(300, 91)
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self.setLabelText(text)

        if icon:
            self.setWindowIcon(icon)

        self.textValueChanged.connect(self._textValueChangedEvent)

    def _textValueChangedEvent(self, string: str):
        if len(string) > self.MAX_TEXT_VALUE_LENGTH:
            self.setTextValue(string[:self.MAX_TEXT_VALUE_LENGTH])

    def initUi(self):
        self.setInputMode(widgets.QInputDialog.InputMode.TextInput)
        self.setWindowFlag(core.Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setModal(True)
        self.setFixedSize(self._size)

    def get_validated_name(self, code: int, name: str) -> Optional[str]:
        if not code:
            return

        if not name:
            return defaultCriticalBox(TEXT.NAME_CANT_BE_EMPTY, self)

        if not validate_filename(name):
            return defaultCriticalBox(
                TEXT.CHARACTERS_CANT_BE_USED.format(characters=" ".join(FILENAME_FORBIDDEN_CHARACTERS)),
                self
            )

        return name

    def setFixedSize(self, a0: core.QSize) -> None:
        self._size = a0

    def resizeEvent(self, event: gui.QResizeEvent) -> None:
        """
        NOTICE: Overriding this method and self.setFixedSize needed because default QInputDialog.setFixedSize
                doesn't work, it only changes fixed width and does not set fixed height, it remains resizable
                (maybe because self.exec() calls self.setFixedSize(defaultQSize))
        """
        if self._size is not None and event.size() != self._size:
            super().setFixedSize(self._size)


class ForAllUsersNewShortcutDialogCheckbox(Widget, widgets.QCheckBox):
    def initUi(self):
        self.setText(TEXT.FOR_ALL_USERS)


class NewShortcutInputDialog(EnterShortcutNameDialog):
    def __init__(self, parent: widgets.QWidget = None, *, icon: gui.QIcon = None):
        super().__init__(TEXT.NEW_SHORTCUT, TEXT.ENTER_NAME, parent, icon=icon)

        self.forAllUsersCheckbox = ForAllUsersNewShortcutDialogCheckbox(self)
        self.setGeometryUi()

    def setGeometryUi(self):
        self.forAllUsersCheckbox.setGeometry(210, 10, 120, 13)


class NewShortcutButton(Widget, widgets.QPushButton):
    def initUi(self):
        self.setIcon(gui.QIcon(resource_path(r'icons\plus-svgrepo-com.png')))
        self.setStyleSheet("""
        QPushButton {
            border: none;
        }""")
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))
        self.setToolTip(TEXT.ADD_NEW_SHORTCUT_TOOL_TIP)

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        if event.button() != core.Qt.MouseButton.LeftButton:
            return

        targetPath = widgets.QFileDialog.getOpenFileName(
            self,
            TEXT.SELECT_FILE,
        )[0]
        if not targetPath:
            return

        iconProvider = widgets.QFileIconProvider()
        dialog = NewShortcutInputDialog(icon=iconProvider.icon(core.QFileInfo(targetPath)))

        if not (name := dialog.get_validated_name(dialog.exec(), dialog.textValue())):
            return

        systemDir, userDir = StartMenu.default_dirs.system, StartMenu.default_dirs.user

        if dialog.forAllUsersCheckbox.isChecked() and not systemDir.is_accessible:
            return defaultCriticalBox(TEXT.NEED_ADMIN_RIGHTS_FOR_CREATE_ALL_USERS_SHORTCUT, dialog)

        shortcutDir = systemDir if dialog.forAllUsersCheckbox.isChecked() else userDir
        core.QFile(targetPath).link(os.path.join(shortcutDir, name + '.lnk'))
        LOG.info(f'Add new shortcut "{name}" in "{shortcutDir}"')
        widgets.QMessageBox.information(dialog, TEXT.COMPLETE, TEXT.SHORTCUT_CREATED)


class RefreshWindowButton(Widget, widgets.QPushButton):
    def __init__(self, mainWindow: 'MainWindow', *args, **kwargs):
        self.mainWindow = mainWindow
        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setIcon(gui.QIcon(resource_path(r'icons\refresh-svgrepo-com.png')))
        self.setStyleSheet("""
        QPushButton {
            border: none;
        }""")
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))
        self.setToolTip(TEXT.REFRESH_WINDOW_TOOL_TIP)

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        if event.button() != core.Qt.MouseButton.LeftButton:
            return

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
        if self.targetPath:
            return self.iconProvider.icon(core.QFileInfo(self.targetPath))

        return self.getIcon()

    def openInExplorer(self):
        subprocess.Popen(f'explorer.exe /select, "{self.shortcut.path}"', shell=True)

    def openTargetInExplorer(self):
        subprocess.Popen(f'explorer.exe /select, "{self.targetPath}"', shell=True)

    def contextMenuEvent(self, event: gui.QContextMenuEvent) -> None:
        menu = widgets.QMenu()
        menu.setStyleSheet('QMenu { color: black; background-color: white; }'
                           'QMenu::item:selected { color: black; background-color: #F0F0F0; }')

        openInExplorerAction = widgets.QAction(gui.QIcon(resource_path('icons/open-shortcut-directory.png')),
                                       TEXT.OPEN_SHORTCUT_PATH, self)
        openTargetInExplorerAction = widgets.QAction(gui.QIcon(resource_path('icons/open-shortcut-target.png')),
                                             TEXT.OPEN_TARGET_PATH, self)
        renameAction = widgets.QAction(gui.QIcon(resource_path('icons/rename-svgrepo-com.png')),
                                       TEXT.RENAME, self)

        menu.addActions([openInExplorerAction, openTargetInExplorerAction])
        menu.addSeparator()
        menu.addAction(renameAction)

        action = menu.exec(event.globalPos())

        if action is openInExplorerAction:
            self.openInExplorer()

        elif action is openTargetInExplorerAction:
            self.openTargetInExplorer()

        elif action is renameAction:
            dialog = EnterShortcutNameDialog(TEXT.RENAME_SHORTCUT, TEXT.ENTER_NAME, icon=self.getIcon())
            dialog.setTextValue(self.shortcut.name)

            if not (name := dialog.get_validated_name(dialog.exec(), dialog.textValue())):
                return

            old_name = self.shortcut.name
            try:
                self.shortcut.rename(name)
            except OSError as e:
                if e.winerror == 5:
                    defaultCriticalBox(TEXT.RENAME_SHORTCUT_NO_ACCESS, dialog)

                else:
                    defaultCriticalBox(TEXT.RENAME_SHORTCUT_ERROR.format(winerror=e.winerror), dialog)

            else:
                self.initUi()
                dialog.setWindowIcon(self.getIcon())
                widgets.QMessageBox.information(
                    dialog,
                    TEXT.COMPLETE,
                    TEXT.SHORTCUT_RENAMED.format(old_name=old_name, new_name=name)
                )


class StartMenuFolderGUI(Widget, widgets.QLabel):
    def __init__(self,
                 folder: SMFolder,
                 guiShortcuts: list[StartMenuShortcutGUI],
                 area: 'ShortcutArea',
                 *args,
                 **kwargs):

        self.folder = folder
        self.guiShortcuts = guiShortcuts
        self.area = area

        self.isKept = None
        self.keptStyleSheet = 'color: #2979FF;'
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

        keepAction = widgets.QAction(TEXT.UNKEEP_FOLDER if self.isKept else TEXT.KEEP_FOLDER, self)

        keepAllFoldersAction = widgets.QAction(self)
        allFoldersIsKept = self.area.allFoldersIsKept()
        keepAllFoldersAction.setText(TEXT.UNKEEP_ALL_FOLDERS if allFoldersIsKept else TEXT.KEEP_ALL_FOLDERS)

        skipAction = widgets.QAction(TEXT.DONT_SKIP_FOLDER if self.isSkipped else TEXT.SKIP_FOLDER, self)

        menu.addActions([
            keepAction,
            keepAllFoldersAction,
            skipAction
        ] if not self.isSkipped else [skipAction])

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
        if event.button() == core.Qt.MouseButton.LeftButton and not self.isSkipped:
            self.reverseKeptState()


class ShortcutArea(Widget, widgets.QScrollArea):
    def __init__(self, folders: list[SMFolder], *args, **kwargs):
        self.folders = folders
        self.guiFolders: list[StartMenuFolderGUI] = []

        self.initWidget = widgets.QWidget()
        self.initLayout = widgets.QVBoxLayout()

        super().__init__(*args, **kwargs)

    def initUi(self):
        self.setVerticalScrollBarPolicy(core.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setStyleSheet(
            """
            QWidget {background-color: #FFFFFF;}
            QScrollBar {background-color: none;}
            QScrollBar::handle:horizontal {background-color: #2979FF;}
            QScrollArea {background-color: #F0F0F0; border: 1px solid #2979FF;}
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


class PathToMoveLabel(Widget, widgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDisabled(True)

    def setDisabled(self, a0: bool) -> None:
        self.setStyleSheet(f'color: {"#808080" if a0 else "#494242"}')
        return super().setDisabled(a0)

    def initUi(self):
        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))  # set cursor: pointer

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        path = widgets.QFileDialog.getExistingDirectory(
            self,
            TEXT.SELECT_FOLDER,
            options=widgets.QFileDialog.Option.ShowDirsOnly
        )

        if not path:
            return

        path = os.path.normpath(path)
        metrics = gui.QFontMetrics(self.font())
        text = metrics.elidedText(path, core.Qt.TextElideMode.ElideLeft, self.width())
        self.setText(text)
        self.setToolTip(HTML(path).wrap_bold())


class MoveToFolderRadioButton(Widget, widgets.QRadioButton):
    def __init__(self, selectPathButton: PathToMoveLabel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toggled.connect(lambda e: selectPathButton.setDisabled(not self.isChecked()))


class RemoveRadioButton(Widget, widgets.QRadioButton):
    def initUi(self):
        self.setChecked(True)


class ApplyToLabel(Widget, widgets.QLabel):
    def initUi(self):
        self.setStyleSheet('color: #54595d;')


class ApplyToCheckedRadioButton(Widget, widgets.QRadioButton):
    def initUi(self):
        self.setChecked(True)


class ApplyToUncheckedRadioButton(Widget, widgets.QRadioButton):
    pass


class ApplyToEmptyFoldersCheckBox(Widget, widgets.QCheckBox):
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
        if event.button() != core.Qt.MouseButton.LeftButton:
            return

        foldersToClean: list[StartMenu.folder_to_clean] = []
        for guiFolder in self.mainWindow.shortcutArea.guiFolders:
            if guiFolder.isSkipped:
                continue

            folderToClean = StartMenu.folder_to_clean(guiFolder.folder, guiFolder.isKept, [], [])
            apply2Checked = self.mainWindow.applyToCheckedRadioButton.isChecked()

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

        if self.mainWindow.moveRadioButton.isChecked():
            path = HTML(self.mainWindow.moveRemovePath2FolderLabel.toolTip()).clear()

            if not path:
                return defaultCriticalBox(TEXT.NEED_SELECT_DIRECTORY, self.parentWidget())

            action = StartMenu.clean_action.move(path)
            actionText = TEXT.MOVED
        else:
            action = StartMenu.clean_action.remove()
            actionText = TEXT.REMOVED

        cleanResult = StartMenu.clean(action, foldersToClean)
        if cleanResult.errors:
            widgets.QMessageBox.warning(
                self.parentWidget(),
                TEXT.WARNING,
                TEXT.HAVE_CLEAN_ERRORS_WARNING.format(
                    errors_count=len(cleanResult.errors),
                    log_fp=cleanResult.log_fp,
                    cleanedFolders=cleanResult.cleaned_folders,
                    appliedShortcuts=cleanResult.applied_shortcuts,
                    actionText=actionText
                )
            )
        else:
            widgets.QMessageBox.information(
                self.parentWidget(),
                TEXT.COMPLETE,
                TEXT.APPLY_CLEANED.format(
                    cleanedFolders=cleanResult.cleaned_folders,
                    appliedShortcuts=cleanResult.applied_shortcuts,
                    actionText=actionText
                )
            )

        update_window(self.mainWindow)


class MainWindow(widgets.QMainWindow):
    def __init__(self):
        super().__init__()

        folders = StartMenu.get_folders()
        emptyFolders = popEmptyFolders(folders)
        self.centralwidget = widgets.QWidget(self)

        self.newShortcutButton = NewShortcutButton(self.centralwidget)
        self.refreshWindowButton = RefreshWindowButton(self, self.centralwidget)

        self.moveRemoveBlock = widgets.QWidget(self.centralwidget)
        self.moveRemovePath2FolderLabel = PathToMoveLabel(self.moveRemoveBlock)
        self.moveRadioButton = MoveToFolderRadioButton(self.moveRemovePath2FolderLabel, self.moveRemoveBlock)
        self.removeRadioButton = RemoveRadioButton(self.moveRemoveBlock)

        self.applyToBlock = widgets.QWidget(self.centralwidget)
        self.applyToLabel = ApplyToLabel(self.applyToBlock)
        self.applyToCheckedRadioButton = ApplyToCheckedRadioButton(self.applyToBlock)
        self.applyToUncheckedRadioButton = ApplyToUncheckedRadioButton(self.applyToBlock)

        self.apply2EmptyFolders = ApplyToEmptyFoldersCheckBox(emptyFolders, self.centralwidget)

        self.applyButton = ApplyButton(self, self.centralwidget)
        self.shortcutArea = ShortcutArea(folders, self.centralwidget)

        self.setFixedSize(core.QSize(402, 317))
        self.setStyleSheet('MainWindow { background-color: #EFEFF1; font-family: Roboto;}')
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi()
        self.setGeometryUi()
        self.setWindowIcon(gui.QIcon(resource_path('icons/menu.ico')))
        core.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        # _translate = core.QCoreApplication.translate

        self.moveRemovePath2FolderLabel.setText(HTML(TEXT.SELECT_DIRECTORY).wrap_underline())
        self.moveRadioButton.setText(TEXT.MOVE_TO_DIRECTORY)
        self.removeRadioButton.setText(TEXT.REMOVE)
        self.applyToLabel.setText(TEXT.APPLY_TO)
        self.applyToCheckedRadioButton.setText(TEXT.SELECTED)
        self.applyToUncheckedRadioButton.setText(TEXT.UNSELECTED)
        self.apply2EmptyFolders.setText(TEXT.APPLY_TO_EMPTY_FOLDERS)
        self.applyButton.setText(TEXT.APPLY)
        self.setWindowTitle(TEXT.MAINWINDOW_TITLE)

    def setGeometryUi(self):
        self.newShortcutButton.setGeometry(11, 5, 14, 14)
        self.refreshWindowButton.setGeometry(34, 5, 14, 14)

        self.moveRemoveBlock.setGeometry(core.QRect(275, 20, 112, 60))
        self.moveRemovePath2FolderLabel.setGeometry(core.QRect(0, 0, 120, 20))
        self.moveRadioButton.setGeometry(core.QRect(0, 20, 120, 20))
        self.removeRadioButton.setGeometry(core.QRect(0, 40, 120, 20))

        self.applyToBlock.setGeometry(core.QRect(275, 85, 120, 60))
        self.applyToLabel.setGeometry(core.QRect(0, 0, 120, 20))
        self.applyToCheckedRadioButton.setGeometry(core.QRect(0, 20, 120, 20))
        self.applyToUncheckedRadioButton.setGeometry(core.QRect(0, 40, 120, 20))

        self.apply2EmptyFolders.setGeometry(core.QRect(275, 150, 120, 30))
        self.applyButton.setGeometry(core.QRect(290, 270, 80, 31))
        self.shortcutArea.setGeometry(core.QRect(10, 25, 250, 275))  # -1px h
