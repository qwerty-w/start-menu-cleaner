from PyQt5.QtCore import QCoreApplication


class AppText:
    CHOOSE_DIRECTORY = 'Choose directory'
    MOVE_TO_DIRECTORY = 'Move to directory'
    DELETE = 'Delete'
    APPLY_TO = 'Apply to'
    SELECTED = 'Selected'
    UNSELECTED = 'Unselected'
    APPLY_TO_EMPTY_FOLDERS = 'Apply to empty\nfolders'
    APPLY = 'Apply'
    WINDOW_TITLE = 'Start Menu Folders Cleaner'
    OPEN_SHORTCUT_PATH = 'Open shortcut path'
    OPEN_TARGET_PATH = 'Open target path'
    KEEP_FOLDER = 'Keep folder'
    UNKEEP_FOLDER = 'Unkeep folder'
    SKIP_FOLDER = 'Skip folder completely'
    DONT_SKIP_FOLDER = 'Don\'t skip folder'

    def __getattr__(self, item):
        return QCoreApplication.translate('MainWindow', self.__dict__.get(item))


TEXT = AppText()
