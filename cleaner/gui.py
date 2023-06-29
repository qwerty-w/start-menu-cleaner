import os
import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from PyQt5 import QtWidgets as widgets
from PyQt5 import QtCore as core
from PyQt5 import QtGui as gui
import qt_material  # after PyQt5 !

from . import log
from .app_text import TEXT
from .menu import StartMenuShortcut, SMFolder, StartMenu
from .utils import resource_path, HTML, validate_filename, FILENAME_FORBIDDEN_CHARACTERS


LOG = log.getLogger(__name__)


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


def setAdjustGeometry(widget: widgets.QWidget, x: int, y: int, w: int = None, h: int = None):
    widget.adjustSize()
    widget.setGeometry(x, y, w if w else widget.width(), h if h else widget.height())


def defaultCriticalBox(text: str, parent: widgets.QWidget = None, title: str = TEXT.ERROR) -> None:
    widgets.QMessageBox.critical(parent, title, text, widgets.QMessageBox.StandardButton.Ok)


class EnterShortcutNameDialog(widgets.QInputDialog):
    MAX_TEXT_VALUE_LENGTH = 200

    def __init__(self, title: str, text: str, parent: widgets.QWidget = None, *, icon: gui.QIcon = None):
        super().__init__(parent=parent)
        self._size = core.QSize(300, 91)

        if icon:
            self.setWindowIcon(icon)
        self.setWindowTitle(title)
        self.setLabelText(text)
        self.setInputMode(widgets.QInputDialog.InputMode.TextInput)
        self.setWindowFlag(core.Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setModal(True)
        self.setFixedSize(self._size)

        # noinspection PyUnresolvedReferences
        self.textValueChanged.connect(self._textValueChangedEvent)

    def _textValueChangedEvent(self, string: str):
        if len(string) > self.MAX_TEXT_VALUE_LENGTH:
            self.setTextValue(string[:self.MAX_TEXT_VALUE_LENGTH])

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


class NewShortcutInputDialog(EnterShortcutNameDialog):
    forALlUsersCheckboxPosition: tuple[int, int] = None

    def __init__(self, parent: widgets.QWidget = None, *, icon: gui.QIcon = None):
        super().__init__(TEXT.NEW_SHORTCUT, TEXT.ENTER_NAME, parent, icon=icon)

        self.forAllUsersCheckbox = widgets.QCheckBox(TEXT.FOR_ALL_USERS, self)
        self.setGeometryUi()

    def setGeometryUi(self):
        if not self.forAllUsersCheckbox:
            raise RuntimeError(f'need to set {type(self)}.forALlUsersCheckboxPosition')

        setAdjustGeometry(self.forAllUsersCheckbox, *self.forALlUsersCheckboxPosition)


class NewShortcutButton(widgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


class RefreshWindowButton(widgets.QPushButton):
    def __init__(self, mainWindow: 'MainWindow', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainWindow = mainWindow

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

        self.mainWindow.refresh()


class StartMenuShortcutGUI(widgets.QCheckBox):
    iconProvider = widgets.QFileIconProvider()

    def __init__(self, shortcut: StartMenuShortcut, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shortcut = shortcut
        rawPath = core.QFileInfo(self.shortcut.path).symLinkTarget()
        self.targetPath = os.path.normpath(rawPath) if rawPath else None

        self.updateUI()

    def updateUI(self):
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
            dialog = EnterShortcutNameDialog(TEXT.RENAME_SHORTCUT, TEXT.ENTER_NAME, icon=self.icon())
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
                self.updateUI()
                dialog.setWindowIcon(self.icon())
                widgets.QMessageBox.information(
                    dialog,
                    TEXT.COMPLETE,
                    TEXT.SHORTCUT_RENAMED.format(old_name=old_name, new_name=name)
                )


class StartMenuFolderGUI(widgets.QLabel):
    def __init__(self,
                 folder: SMFolder,
                 guiShortcuts: list[StartMenuShortcutGUI],
                 area: 'ShortcutArea',
                 *args,
                 **kwargs):
        super().__init__(area, *args, **kwargs)

        self.folder = folder
        self.guiShortcuts = guiShortcuts
        self.area = area

        self.isKept = None
        self.keptStyleSheet = 'color: #2979FF;'
        self.notKeptStyleSheet = 'color: #54595d;'

        self.isSkipped = None
        self.isKeptBeforeSkipping = None

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


class ShortcutArea(widgets.QScrollArea):  # todo: move displayShortcuts and other to __init__/initUi
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.folders = StartMenu.get_folders()
        self.emptyFolders = self.popEmptyFolders()

        self.guiFolders: list[StartMenuFolderGUI] = []
        self.initWidget = widgets.QWidget()
        self.initLayout = widgets.QVBoxLayout()

        self.setVerticalScrollBarPolicy(core.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setStyleSheet('QScrollArea {background-color: #F0F0F0; border: 1px solid #2979FF;}')
        self.initWidget.setStyleSheet('QWidget {background-color: #FFFFFF;}')
        self.displayShortcuts()

    def popEmptyFolders(self) -> list[SMFolder]:
        e, index = [], 0

        while index < len(self.folders):
            if self.folders[index].is_empty():
                e.append(self.folders.pop(index))
                continue

            index += 1

        return e

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


class PathToMoveLabel(widgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDisabled(True)

        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))  # set cursor: pointer

    def setDisabled(self, a0: bool) -> None:
        self.setStyleSheet(f'color: {"#808080" if a0 else "#494242"}')
        return super().setDisabled(a0)

    def mousePressEvent(self, event: gui.QMouseEvent) -> None:
        path = widgets.QFileDialog.getExistingDirectory(
            self,
            TEXT.SELECT_FOLDER,
            options=widgets.QFileDialog.Option.ShowDirsOnly
        )

        if not path:
            return

        fname = os.path.basename(os.path.normpath(path))
        metrics = gui.QFontMetrics(self.font())
        text = metrics.elidedText(f'{TEXT.DIRECTORY}: {fname}', core.Qt.TextElideMode.ElideRight, self.width())
        self.setText(text)
        self.setToolTip(HTML(path).wrap_bold())


class MoveToFolderRadioButton(widgets.QRadioButton):
    def __init__(self, selectPathButton: PathToMoveLabel, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # noinspection PyUnresolvedReferences
        self.toggled.connect(lambda e: selectPathButton.setDisabled(not self.isChecked()))


class RemoveRadioButton(widgets.QRadioButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setChecked(True)


class ApplyToLabel(widgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet('color: #54595d;')


class ApplyToCheckedRadioButton(widgets.QRadioButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setChecked(True)


class ApplyToEmptyFoldersCheckBox(widgets.QCheckBox):
    def __init__(self, emptyFolders: list[SMFolder], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.emptyFolders = emptyFolders

        tip = TEXT.NO_EMPTY_FOLDERS if not self.emptyFolders else ', '.join(f'"{x.name}"' for x in self.emptyFolders)
        self.setToolTip(tip)


class ApplyButton(widgets.QPushButton):
    def __init__(self, mainWindow: 'MainWindow', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mainWindow = mainWindow

        self.setCursor(gui.QCursor(core.Qt.CursorShape.PointingHandCursor))

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
            path = HTML(self.mainWindow.moveRemovePathToMoveLabel.toolTip()).clear()

            if not path:
                return defaultCriticalBox(TEXT.NEED_SELECT_DIRECTORY, self)

            action = StartMenu.clean_action.move(path)
            actionText = TEXT.MOVED
        else:
            action = StartMenu.clean_action.remove()
            actionText = TEXT.REMOVED

        cleanResult = StartMenu.clean(action, foldersToClean)
        if cleanResult.errors:
            widgets.QMessageBox.warning(
                self,
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
                self,
                TEXT.COMPLETE,
                TEXT.APPLY_CLEANED.format(
                    cleanedFolders=cleanResult.cleaned_folders,
                    appliedShortcuts=cleanResult.applied_shortcuts,
                    actionText=actionText
                )
            )
        self.mainWindow.refresh()


class Stylist(ABC):
    def __init__(self, app: widgets.QApplication, mainWindow: 'MainWindow'):
        self.app = app
        self.mw = mainWindow

    def common(self):
        self.mw.newShortcutButton.setGeometry(11, 5, 14, 14)
        self.mw.refreshWindowButton.setGeometry(34, 5, 14, 14)

        self.mw.shortcutArea.setGeometry(10, 25, 250, 275)  # -1px h

    @abstractmethod
    def _apply(self):
        raise NotImplemented

    def apply(self):
        self.common()
        self._apply()


class ClassicStylist(Stylist):
    def _apply(self):
        self.mw.setFixedSize(402, 317)
        self.mw.setStyleSheet('MainWindow { background-color: #EFEFF1; font-family: Roboto; }')

        # for all users button
        NewShortcutInputDialog.forALlUsersCheckboxPosition = 210, 10

        # right buttons
        #     move or remove
        self.mw.moveRemoveBlock.setGeometry(275, 20, 112, 60)
        setAdjustGeometry(self.mw.moveRemovePathToMoveLabel, 0, 0)
        setAdjustGeometry(self.mw.moveRadioButton, 0, 20, h=20)
        setAdjustGeometry(self.mw.removeRadioButton, 0, 40, h=20)

        #     to checked or to unchecked
        self.mw.applyToBlock.setGeometry(275, 85, 112, 60)
        setAdjustGeometry(self.mw.applyToLabel, 0, 0)
        setAdjustGeometry(self.mw.applyToCheckedRadioButton, 0, 20, h=20)
        setAdjustGeometry(self.mw.applyToUncheckedRadioButton, 0, 40, h=20)

        #     empty folders
        setAdjustGeometry(self.mw.apply2EmptyFolders, 275, 150)

        # apply
        self.mw.applyButton.setGeometry(290, 270, 80, 31)


class MaterialStylist(Stylist):
    _APP_WRAPPED = False

    def _apply(self):
        self.mw.setFixedSize(405, 317)
        self.mw.centralwidget.setStyleSheet('background-color: #EFEFF1')
        self.mw.shortcutArea.initLayout.setSpacing(0)

        # for all users button
        NewShortcutInputDialog.forALlUsersCheckboxPosition = 194, 1

        # right buttons
        #     move or remove
        self.mw.moveRemoveBlock.setGeometry(270, 20, 122, 57)
        setAdjustGeometry(self.mw.moveRemovePathToMoveLabel, 3, 0)
        setAdjustGeometry(self.mw.moveRadioButton, 0, 17, 122, 20)
        setAdjustGeometry(self.mw.removeRadioButton, 0, 37, 100, 20)

        #     apply to checked or unchecked
        self.mw.applyToBlock.setGeometry(270, 82, 122, 57)
        setAdjustGeometry(self.mw.applyToLabel, 3, 0)
        setAdjustGeometry(self.mw.applyToCheckedRadioButton, 0, 17, 100, 20)
        setAdjustGeometry(self.mw.applyToUncheckedRadioButton, 0, 37, 100, 20)

        #     empty folders
        setAdjustGeometry(self.mw.apply2EmptyFolders, 270, 150, 115)

        # apply
        self.mw.applyButton.setGeometry(292, 270, 80, 31)

        if not self._APP_WRAPPED:
            qt_material.apply_stylesheet(self.app, theme='light_blue.xml', extra={'density_scale': '-1'})
            type(self)._APP_WRAPPED = True

            # remove focus
            self.app.setStyleSheet(self.app.styleSheet() + """
                                      QPushButton:focus,
                                      QPushButton:flat:focus,
                                      QPushButton:pressed:focus
                                      QPushButton:checked:focus,
                                      QMenu::indicator:focus,
                                      QRadioButton::indicator:focus,
                                      QCheckBox::indicator:focus
                                      {
                                          background-color: none;
                                      }""")


class Style(Enum):
    CLASSIC = ClassicStylist
    MATERIAL = MaterialStylist


class MainWindow(widgets.QMainWindow):
    def __init__(self, app: widgets.QApplication, style: Style):
        super().__init__()
        self.app = app
        self.window_style = style

        self.centralwidget = widgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.newShortcutButton = NewShortcutButton(self.centralwidget)
        self.refreshWindowButton = RefreshWindowButton(self, self.centralwidget)

        self.shortcutArea = ShortcutArea(self.centralwidget)

        self.moveRemoveBlock = widgets.QWidget(self.centralwidget)
        self.moveRemovePathToMoveLabel = PathToMoveLabel(self.moveRemoveBlock)
        self.moveRadioButton = MoveToFolderRadioButton(self.moveRemovePathToMoveLabel, self.moveRemoveBlock)
        self.removeRadioButton = RemoveRadioButton(self.moveRemoveBlock)

        self.applyToBlock = widgets.QWidget(self.centralwidget)
        self.applyToLabel = ApplyToLabel(self.applyToBlock)
        self.applyToCheckedRadioButton = ApplyToCheckedRadioButton(self.applyToBlock)
        self.applyToUncheckedRadioButton = widgets.QRadioButton(self.applyToBlock)

        self.apply2EmptyFolders = ApplyToEmptyFoldersCheckBox(self.shortcutArea.emptyFolders, self.centralwidget)

        self.applyButton = ApplyButton(self, self.centralwidget)

        self.retranslateUi()
        self.window_style.value(self.app, self).apply()  # apply styles for app and MainWindow
        self.setWindowIcon(gui.QIcon(resource_path('icons/menu.ico')))
        core.QMetaObject.connectSlotsByName(self)

    def refresh(self) -> 'MainWindow':
        LOG.info('Update window')

        pos = self.pos()
        self.close()

        StartMenu.update()
        w = MainWindow(self.app, self.window_style)
        w.move(pos)
        w.show()
        return w

    def retranslateUi(self):
        self.moveRemovePathToMoveLabel.setText(HTML(TEXT.SELECT_DIRECTORY).wrap_underline())
        self.moveRadioButton.setText(TEXT.MOVE_TO_DIRECTORY)
        self.removeRadioButton.setText(TEXT.REMOVE)

        self.applyToLabel.setText(TEXT.APPLY_TO)
        self.applyToCheckedRadioButton.setText(TEXT.SELECTED)
        self.applyToUncheckedRadioButton.setText(TEXT.UNSELECTED)

        self.apply2EmptyFolders.setText(TEXT.APPLY_TO_EMPTY_FOLDERS)

        self.applyButton.setText(TEXT.APPLY)

        self.setWindowTitle(TEXT.MAINWINDOW_TITLE)
