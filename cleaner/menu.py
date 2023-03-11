import os
import time
import struct
import locale
import logging
import tempfile
from typing import Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections import namedtuple

from send2trash import send2trash

from . import utils


class StartMenuDir(os.PathLike):
    def __init__(self, path: str, type: str):
        self.path = path
        self.type = type
        self.is_accessible = self._check_on_accessible()

    def _check_on_accessible(self) -> bool:
        tmp_f = os.path.join(self.path, 'tmp.tmp')

        try:
            open(tmp_f, mode='w')
            os.remove(tmp_f)
        except OSError:
            return False

        return True

    def __str__(self) -> str:
        return self.path

    def __fspath__(self) -> str:
        return self.path

    def update_accessibility(self):
        self.is_accessible = self._check_on_accessible()


class SMObject(ABC):
    path: str
    name: str

    @abstractmethod
    def move(self, path_to_directory: str) -> None:
        ...

    @abstractmethod
    def remove(self) -> None:
        ...


class SMFolder(SMObject, ABC):
    name: str
    shortcuts: list['StartMenuShortcut']

    def is_empty(self):
        return len(self.shortcuts) == 0


class StartMenuFolder(SMFolder):
    def __init__(self, path: str, *, shortcuts: list['StartMenuShortcut'] = None):
        self.path: str = path
        self.name = os.path.basename(path)
        self.shortcuts = self._get_shortcuts() if not shortcuts else shortcuts

    def __repr__(self, indent: int = 4):
        indent_text = ' ' * indent
        # first \n need for correct display print(list[StartMenuFolder])
        return f'\n{self.name}\n' + '\n'.join(indent_text + shortcut.name for shortcut in self.shortcuts)

    def _get_shortcuts(self) -> list['StartMenuShortcut']:
        return [
            StartMenuShortcut(os.path.join(dir_data[0], sc))
            for dir_data in list(os.walk(self.path))
            for sc in dir_data[2] if os.path.splitext(sc)[-1] in ('.lnk', '.url')
        ]

    def update_shortcuts(self):
        self.shortcuts = self._get_shortcuts()

    def copy(self):
        return type(self)(self.path, shortcuts=self.shortcuts)

    def move(self, path_to_directory: str) -> None:
        new_p = os.path.join(path_to_directory, self.name)

        if os.path.exists(new_p):
            try:
                os.remove(new_p)
            except OSError:
                return send2trash(self.path)

        utils.rmove_dir(self.path, path_to_directory, replace=False)
        self.path = new_p

    def remove(self) -> None:
        send2trash(self.path)


class StartMenuExtendedFolder(SMFolder):  # folder which exists in few start menu dirs
    def __init__(self, folders: list[SMFolder]):
        self.folders = []
        self.name = folders[0].name
        self.shortcuts = []

        for index, folder in enumerate(folders):
            if self.name != folder.name:
                raise ValueError('folders names must be same')

            self.shortcuts.extend(folder.shortcuts)

            if isinstance(folder, self.__class__):
                self.folders.extend(folder.folders)
            else:
                self.folders.append(folder)

    def move(self, path_to_directory: str) -> None:
        for f in self.folders:
            f.move(path_to_directory)

    def remove(self) -> None:
        for f in self.folders:
            f.remove()


class StartMenuShortcut(SMObject):
    def __init__(self, ph: str):
        self.path: str = ph
        self.name, self.ext = os.path.splitext(os.path.basename(ph))

    def __repr__(self):
        return self.path

    def get_rpath(self):  # get relative path
        fpath = self.get_fpath()
        return self.path[len(fpath) + 1:]

    def get_fpath(self):  # get SM folder path
        for d in StartMenu.default_dirs:
            if os.path.commonpath([d.path, self.path]) == d.path:
                return d.path

        raise ValueError('StartMenuShortcut.path does not belong to any dir from DEFAULT_START_MENU_SHORTCUTS_DIRS')

    def move(self, path_to_directory: str):
        new_p = os.path.join(path_to_directory, self.name + self.ext)
        os.replace(self.path, new_p)
        self.path = new_p

    def relative_move(self, path_to_directory: str):
        new_path_to_dir = os.path.join(path_to_directory, os.path.split(self.get_rpath())[0])
        if not os.path.exists(new_path_to_dir):
            utils.safe_mkdirs(new_path_to_dir)

        self.move(new_path_to_dir)

    def remove(self):
        send2trash(self.path)

    def get_link_target(self) -> str:
        with open(self.path, 'rb') as stream:
            content = stream.read()
            # skip first 20 bytes (HeaderSize and LinkCLSID)
            # read the LinkFlags structure (4 bytes)
            lflags = struct.unpack('I', content[0x14:0x18])[0]
            position = 0x18
            # if the HasLinkTargetIDList bit is set then skip the stored IDList
            # structure and header
            if (lflags & 0x01) == 1:
                position = struct.unpack('H', content[0x4C:0x4E])[0] + 0x4E
            last_pos = position
            position += 0x04
            # get how long the file information is (LinkInfoSize)
            length = struct.unpack('I', content[last_pos:position])[0]
            # skip 12 bytes (LinkInfoHeaderSize, LinkInfoFlags and VolumeIDOffset)
            position += 0x0C
            # go to the LocalBasePath position
            lbpos = struct.unpack('I', content[position:position + 0x04])[0]
            position = last_pos + lbpos
            # read the string at the given position of the determined length
            size = (length + last_pos) - position - 0x02
            content = content[position:position + size].split(b'\x00', 1)
            return content[-1].decode('utf-16' if len(content) > 1 else locale.getdefaultlocale()[1])


class CleanError(Exception):
    def __init__(self, e: Exception):
        self.during_e = e
        self.__traceback__ = e.__traceback__

    def __str__(self):
        return f'[{self.during_e.__class__.__name__}: {self.during_e}]'

    def represent(self):
        return f'{self.__class__.__name__}: {str(self)}'


class ShortcutToApplyHandleError(CleanError):
    pass


class ShortcutToSaveHandleError(CleanError):
    pass


class FolderHandleError(CleanError):
    pass


class _CleanAction:
    MOVE = 0
    REMOVE = 1

    def __init__(self, id: int, name: str, data: dict = None):
        self.id = id
        self.name = name
        self.data = {} if data is None else data

    def __int__(self):
        return self.id

    def __eq__(self, other):
        try:
            other = int(other)
        except TypeError:
            pass

        return int(self) == other

    @classmethod
    def move(cls, path: str):
        return cls(cls.MOVE, 'move', {'path': path, 'ps': 'moved'})

    @classmethod
    def remove(cls):
        return cls(cls.REMOVE, 'remove', {'ps': 'removed'})

    @classmethod
    def get_ints(cls):
        return [
            cls.MOVE,
            cls.REMOVE
        ]


@dataclass
class _FolderToClean:
    folder: SMFolder
    is_kept: bool
    shortcuts_to_apply: list[StartMenuShortcut]
    shortcuts_to_save: list[StartMenuShortcut]


@dataclass
class _CleanResult:
    cleaned_folders: int = 0
    applied_shortcuts: int = 0
    errors: list[CleanError] = field(default_factory=lambda: [])
    log_fp: str = ''


class _CleanLogger(logging.Logger):
    KEEP_LOG_FILE = False

    def __init__(self, name: str, level: int = logging.INFO):
        super().__init__(name, level)
        self.default_formatter = logging.Formatter('[{asctime}] {folder_name}{message}', '%H:%M:%S', '{')

        std = logging.StreamHandler()
        std.setFormatter(self.default_formatter)
        self.addHandler(std)

        self.file: Optional[logging.FileHandler] = None
        self.manager = logging.Logger.manager
        self.manager.loggerDict[self.name] = self
        self.manager._fixupParents(self)
        self.propagate = False

    def _log(self, level: int, msg: object, *args, extra: dict = None, **kwargs) -> None:
        extra = extra.copy() if extra else {}
        folder_name = extra.get('folder_name') or kwargs.get('folder_name') or kwargs.get('folder')
        extra['folder_name'] = f'{folder_name} -> ' if folder_name else ''
        return super()._log(level, msg, *args, extra=extra, **kwargs)

    def init_file(self):
        name = f'sm-clean-{int(time.time())}.log'
        self.file = logging.FileHandler(os.path.join(tempfile.gettempdir(), name))
        self.file.setFormatter(self.default_formatter)
        self.addHandler(self.file)

        self.info(f'Create .log file (by clean-init): {name}')

    def reset_file(self, *, keep_file: bool = True, keep_reason: str = 'default'):
        if not self.file:
            return

        f_name = os.path.basename(self.file.baseFilename)
        msg = '{} .log file (by clean-{}): ' + f_name

        if self.KEEP_LOG_FILE:
            self.info(msg.format('Keep', 'KEEP_LOG_FILE'))

        elif keep_file:
            self.info(msg.format('Keep', keep_reason))

        self.removeHandler(self.file)
        self.file.close()

        if not self.KEEP_LOG_FILE and not keep_file:
            os.remove(self.file.baseFilename)
            self.info(msg.format('Delete', 'reset'))

        self.file = None


class SMCleaner:
    actions = _CleanAction
    folder = _FolderToClean

    LOG = _CleanLogger(__name__ + '.clean')
    L_START_CLEAN = '=== START CLEAN ==='
    L_ACTION = 'ACTION - <{}>'
    L_START_FOLDER = '-- Start folder --'
    L_HAVE_ERROR_WITH_SHORTCUT = 'Have an error with <{}> shortcut'
    L_SHORTCUT_HANDLED = 'Shortcut "{}" was {}'
    L_KEEP_FOLDER = 'Folder was kept'
    L_SHORTCUT_MOVED_OUT = 'Shortcut "{}" was moved out'
    L_FOLDER_HANDLED = 'Folder was {}'
    L_FOLDER_END = '-- Folder end --'
    L_CLEAN_HANDLED = '{} folders were cleaned, {} shortcuts were {}'
    L_END_CLEAN = '=== END CLEAN ==='

    def __init__(self, action: _CleanAction, folders_to_clean: list[_FolderToClean]):
        if action not in self.actions.get_ints():
            raise ValueError('action should be equal _CleanAction actions')

        self.action = action
        self.folders2clean = folders_to_clean
        self.result: _CleanResult = _CleanResult(0, 0, [])

    def handle_e(self, e: CleanError, *, msg: str = None, extra: dict = None):
        self.result.errors.append(e)
        self.LOG.error('Have an error:' if msg is None else msg, exc_info=e, extra=extra)

    def clean(self):
        self.LOG.init_file()

        is_move = self.action == self.actions.MOVE
        is_remove = self.action == self.actions.REMOVE
        action_ps = self.action.data['ps']

        self.LOG.info(self.L_START_CLEAN)
        self.LOG.info(self.L_ACTION.format(self.action.name.upper()))

        for clean_f in self.folders2clean:
            extra = {'folder_name': clean_f.folder.name}
            self.LOG.info(self.L_START_FOLDER)

            # handle selected shortcuts
            for clean_s in clean_f.shortcuts_to_apply:
                try:
                    if is_move:
                        clean_s.relative_move(self.action.data['path'])

                    elif is_remove:
                        clean_s.remove()

                except Exception as e:
                    self.handle_e(
                        ShortcutToApplyHandleError(e),
                        msg=self.L_HAVE_ERROR_WITH_SHORTCUT.format(clean_s.name),
                        extra=extra
                    )
                    continue

                self.result.applied_shortcuts += 1
                self.LOG.info(self.L_SHORTCUT_HANDLED.format(clean_s.name, action_ps), extra=extra)

            # skip folder if it's kept
            if clean_f.is_kept:
                self.LOG.info(self.L_KEEP_FOLDER, extra=extra)
                continue

            # move out saved shortcuts
            skip_folder = False
            for saved_s in clean_f.shortcuts_to_save:
                try:
                    saved_s.move(saved_s.get_fpath())
                    self.LOG.info(self.L_SHORTCUT_MOVED_OUT.format(saved_s.name), extra=extra)
                    self.result.applied_shortcuts += 1

                except OSError as e:
                    self.handle_e(
                        ShortcutToSaveHandleError(e),
                        msg=self.L_HAVE_ERROR_WITH_SHORTCUT.format(saved_s.name),
                        extra=extra
                    )
                    skip_folder = True
                    break

            if skip_folder:
                continue

            # handle folder after saving remaining shortcuts (by moving out to common folder)
            try:
                if is_move:
                    clean_f.folder.move(self.action.data['path'])

                elif is_remove:
                    clean_f.folder.remove()

                self.LOG.info(self.L_FOLDER_HANDLED.format(action_ps), extra=extra)
                self.LOG.info(self.L_FOLDER_END)

            except OSError as e:
                self.handle_e(FolderHandleError(e), extra=extra)

        self.LOG.info(self.L_CLEAN_HANDLED.format(
            self.result.cleaned_folders,
            self.result.applied_shortcuts,
            action_ps
        ))
        self.LOG.info(self.L_END_CLEAN)
        self.result.log_fp = self.LOG.file.baseFilename
        self.LOG.reset_file(keep_file=bool(self.result.errors), keep_reason='errors')
        return self.result


class StartMenu:
    clean_action = _CleanAction
    folder_to_clean = _FolderToClean
    clean_result = _CleanResult

    default_dirs = namedtuple('_SMDirs', 'system user')(
        StartMenuDir(
            os.path.join(os.getenv('SystemDrive'), r'\ProgramData\Microsoft\Windows\Start Menu\Programs'),
            'system'
        ),
        StartMenuDir(
            os.path.join(os.getenv('AppData'), r'Microsoft\Windows\Start Menu\Programs'),
            'user'
        )
    )

    @classmethod
    def update(cls) -> None:
        for d in cls.default_dirs:
            d.update_accessibility()

    @classmethod
    def get_folders(cls) -> list[SMFolder]:
        folders = []

        for sm_dir in cls.default_dirs:
            if not sm_dir.is_accessible:
                continue

            for item in os.listdir(sm_dir.path):
                full_path = os.path.join(sm_dir.path, item)

                if not os.path.isdir(full_path):
                    continue

                new_folder = StartMenuFolder(path=full_path)
                for index, folder in enumerate(folders):
                    if folder.name == new_folder.name:
                        folders[index] = StartMenuExtendedFolder([folder, new_folder])
                        break

                else:
                    folders.append(new_folder)

        folders.sort(key=lambda x: x.name.lower())
        return folders

    @classmethod
    def clean(cls, action: _CleanAction, folders_to_clean: list[_FolderToClean]) -> _CleanResult:
        return SMCleaner(action, folders_to_clean).clean()
