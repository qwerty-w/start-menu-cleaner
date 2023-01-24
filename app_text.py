from PyQt5.QtCore import QCoreApplication


class AppText:
    SELECT_DIRECTORY = 'Select a directory'
    SELECT_FOLDER = 'Select a folder:'
    SELECT_FILE = 'Select a file:'
    MOVE_TO_DIRECTORY = 'Move to directory'
    DELETE = 'Delete'
    APPLY_TO = 'Apply to shortcuts:'
    SELECTED = 'Checked'
    UNSELECTED = 'Unchecked'
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
    NEED_ADMIN_PRIVILEGES_FOR_ALL_USERS_SHORTCUT = 'To add shortcut for all users need admin privileges'
    COMPLETE = 'Complete'
    SHORTCUT_CREATED = 'Shortcut was successfully created'
    KEEP_ALL_FOLDERS = 'Keep all folders'
    UNKEEP_ALL_FOLDERS = 'Unkeep all folders'
    APPLY_CLEANED = 'Were cleaned {cleanedFolders} folders and {appliedShortcuts} shortcuts were {actionText}'
    NEED_SELECT_DIRECTORY = 'You have to select a directory to move the shortcuts to it'
    MOVED = 'moved'
    DELETED = 'deleted'
    ADD_NEW_SHORTCUT_TOOL_TIP = 'Add new shortcut'
    REFRESH_WINDOW_TOOL_TIP = 'Update shortcuts list'

    def __getattr__(self, item):
        return QCoreApplication.translate('MainWindow', self.__dict__.get(item))


TEXT = AppText()
