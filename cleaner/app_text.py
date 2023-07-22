from .config import CONFIG


class EN:
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
    DIRECTORY = 'Directory'
    QUESTION = 'Question'
    INFO = 'Info'
    CHANGE_LANGUAGE = 'Change language'


class RU:
    SELECT_DIRECTORY = 'Выбрать папку'
    SELECT_FOLDER = 'Выберите директорию:'
    SELECT_FILE = 'Выберите файл:'
    MOVE_TO_DIRECTORY = 'Переместить'
    REMOVE = 'Удалить'
    APPLY_TO = 'Применить к:'
    SELECTED = 'Отмеченным'
    UNSELECTED = 'Неотмеченным'
    APPLY_TO_EMPTY_FOLDERS = 'Применить к\nпустым папкам'
    APPLY = 'Очистить'
    MAINWINDOW_TITLE = 'Start Menu Cleaner'
    OPEN_SHORTCUT_PATH = 'Показать папку ярлыка'
    OPEN_TARGET_PATH = 'Показать таргет ярлыка'
    KEEP_FOLDER = 'Оставить папку'
    UNKEEP_FOLDER = 'Не оставлять папку'
    SKIP_FOLDER = 'Полностью пропустить'
    DONT_SKIP_FOLDER = 'Не пропускать'
    FOR_ALL_USERS = 'Для всех пользователей'
    ENTER_NAME = 'Введите имя:'
    NEW_SHORTCUT = 'Новый ярлык'
    ERROR = 'Ошибка'
    NAME_CANT_BE_EMPTY = 'Имя не может быть пустым'
    CHARACTERS_CANT_BE_USED = 'Символы {characters} не могут быть использованы'
    NEED_ADMIN_RIGHTS_FOR_CREATE_ALL_USERS_SHORTCUT = 'Для того чтобы создать ярлык для всех пользователей требуются ' \
                                                      'права администратора'
    COMPLETE = 'Успешно'
    SHORTCUT_CREATED = 'Ярлык был успешно создан'
    KEEP_ALL_FOLDERS = 'Оставить все папки'
    UNKEEP_ALL_FOLDERS = 'Не оставлять все папки'
    APPLY_CLEANED = 'Было очищено {cleanedFolders} папок, {appliedShortcuts} ярлыков было {actionText}'
    NEED_SELECT_DIRECTORY = 'Вы должны выбрать директорию для того что переместить ярлыки в неё'
    MOVED = 'перемещено'
    REMOVED = 'удалено'
    ADD_NEW_SHORTCUT_TOOL_TIP = 'Новый ярлык'
    REFRESH_WINDOW_TOOL_TIP = 'Обновить'
    NO_EMPTY_FOLDERS = 'Нет пустых папок'
    NO_ACCESS_WARNING = 'Нет доступа'
    NEED_ADMIN_RIGHTS_FOR_ALL_USERS_SM_PATH = \
        '{sys_d}\n\nЯрлыки для всех пользователей не будут отображаться, потому что находятся в директории с ' \
        'повышенным уровнем доступа. Измените права доступа для директории и её подпапок или запустите приложение ' \
        'от имени администратора'
    NO_ACCESS_TO_DIR = '{dirs}\n\nНет доступа к директории. Её ярлыки не будут отображены. Измените права доступа ' \
                       'для директории её подпапок или запустите приложение от имени администратора'
    NO_ACCESS_TO_DIRS = '{dirs}\n\nНет доступа к директориям. Их ярлыки не будут отображены. Измените права доступа ' \
                        'для директорий и их подпапок или запустите приложение от имени администратора'
    WARNING = 'Предупреждение'
    HAVE_CLEAN_ERRORS_WARNING = 'Во время очистки, было вызвано {errors_count} ошибок, более детальную информацию ' \
                                'можно найти в лог-файле ({log_fp}).\nРезультат - {cleanedFolders} папок и ' \
                                '{appliedShortcuts} ярлыков было {actionText}'
    RENAME = 'Переименовать'
    RENAME_SHORTCUT = 'Переименовать ярлык'
    SHORTCUT_RENAMED = 'Ярлык "{old_name}" был переименован в "{new_name}"'
    RENAME_SHORTCUT_NO_ACCESS = 'Нет доступа. Попробуйте запустить приложение с правами администратора'
    RENAME_SHORTCUT_ERROR = 'Невозможно переименовать ярлык: winerror #{winerror}'
    DIRECTORY = 'Директория'
    QUESTION = 'Вопрос'
    INFO = 'Информация'
    CHANGE_LANGUAGE = 'Изменить язык'


class _text:
    def __getattr__(self, item):
        return getattr(RU, item) if CONFIG['opt']['lang'] == 'ru' else getattr(EN, item)


TEXT = _text()
