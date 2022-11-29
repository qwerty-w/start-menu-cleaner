from PyQt5.QtCore import QCoreApplication


class AppText:
    SELECT_DIRECTORY = 'Select a directory'
    SELECT_FOLDER = 'Select a folder:'
    SELECT_FILE = 'Select a file:'
    MOVE_TO_DIRECTORY = 'Move to directory'
    DELETE = 'Delete'
    APPLY_TO = 'Apply to'
    SELECTED = 'Selected'
    UNSELECTED = 'Unselected'
    APPLY_TO_EMPTY_FOLDERS = 'Apply to empty\nfolders'
    APPLY = 'Apply'
    WINDOW_TITLE = 'Start Menu Folders Cleaner'
    OPEN_SHORTCUT_PATH = 'Open shortcut path in explorer'
    OPEN_TARGET_PATH = 'Open target path in explorer'
    KEEP_FOLDER = 'Keep folder'
    UNKEEP_FOLDER = 'Unkeep folder'
    SKIP_FOLDER = 'Skip folder completely'
    DONT_SKIP_FOLDER = 'Don\'t skip folder'
    FOR_ALL_USERS = 'For all users'
    ENTER_NAME = 'Enter name:'
    NEW_SHORTCUT = 'New shortcut'
    ERROR = 'Error'
    NAME_CANT_BE_EMPTY = 'Name can\'t be empty'
    CHARACTERS_CANT_BE_USED = 'Characters {characters} cannot be used'
    NEED_ADMIN_PRIVILEGES = 'Need admin privileges'
    COMPLETE = 'Complete'
    SHORTCUT_CREATED = 'Shortcut was successfully created'\

    def __getattr__(self, item):
        return QCoreApplication.translate('MainWindow', self.__dict__.get(item))


TEXT = AppText()
