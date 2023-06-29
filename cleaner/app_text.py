from PyQt5.QtCore import QCoreApplication


class AppText:
    SELECT_DIRECTORY = 'Select a directory'
    SELECT_FOLDER = 'Select a folder:'
    SELECT_FILE = 'Select a file:'
    MOVE_TO_DIRECTORY = 'Move to directory'
    REMOVE = 'Remove'
    APPLY_TO = 'Apply to shortcuts:'
    SELECTED = 'Checked'
    UNSELECTED = 'Unchecked'
    APPLY_TO_EMPTY_FOLDERS = 'Apply to empty\nfolders'
    APPLY = 'Apply'
    MAINWINDOW_TITLE = 'Start Menu Cleaner'
    OPEN_SHORTCUT_PATH = 'Open shortcut directory in explorer'
    OPEN_TARGET_PATH = 'Open target in explorer'
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
    NEED_ADMIN_RIGHTS_FOR_CREATE_ALL_USERS_SHORTCUT = 'To create shortcut for all users need admin rights ' \
                                                      '(run app as admin)'
    COMPLETE = 'Complete'
    SHORTCUT_CREATED = 'Shortcut was successfully created'
    KEEP_ALL_FOLDERS = 'Keep all folders'
    UNKEEP_ALL_FOLDERS = 'Unkeep all folders'
    APPLY_CLEANED = 'Were cleaned {cleanedFolders} folders and {appliedShortcuts} shortcuts were {actionText}'
    NEED_SELECT_DIRECTORY = 'You have to select a directory to move the shortcuts to it'
    MOVED = 'moved'
    REMOVED = 'removed'
    ADD_NEW_SHORTCUT_TOOL_TIP = 'Add new shortcut'
    REFRESH_WINDOW_TOOL_TIP = 'Update shortcuts list'
    NO_EMPTY_FOLDERS = 'No empty folders'
    NO_ACCESS_WARNING = 'No access warning'
    NEED_ADMIN_RIGHTS_FOR_ALL_USERS_SM_PATH = \
        '{sys_d}\n\nShortcuts installed for all users will not be displayed because they are located in a directory' \
        ' with an elevated access level. Change the directory permissions and its subfolders or run the application' \
        ' with administrator rights'
    NO_ACCESS_TO_DIR = '{dirs}\n\nNo access to this shortcut directory. Its shortcuts will not be displayed. ' \
                       'Change the directory permissions and its subfolders or run the application with ' \
                       'administrator rights'
    NO_ACCESS_TO_DIRS = '{dirs}\n\nNo access to these shortcut directories. Their shortcuts will not be displayed. ' \
                        'Change the directories permissions and its subfolders or run the application with ' \
                        'administrator rights'
    WARNING = 'Warning'
    HAVE_CLEAN_ERRORS_WARNING = 'During the cleanup, {errors_count} errors were caused, more information about ' \
                                'them can be found in the log file ({log_fp}).\nResult - {cleanedFolders} ' \
                                'folders and {appliedShortcuts} shortcuts were {actionText}'
    RENAME = 'Rename'
    RENAME_SHORTCUT = 'Rename shortcut'
    SHORTCUT_RENAMED = 'Shortcut "{old_name}" was renamed to "{new_name}"'
    RENAME_SHORTCUT_NO_ACCESS = 'Access denied. Try to run application with administrator rights'
    RENAME_SHORTCUT_ERROR = 'Unable to rename shortcut: winerror #{winerror}'


    def __getattr__(self, item):
        return QCoreApplication.translate('MainWindow', self.__dict__.get(item))


TEXT = AppText()
