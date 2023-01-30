import os
import struct
import locale
import logging
from dataclasses import dataclass
from collections import namedtuple
from abc import ABC, abstractmethod


LOG = logging.getLogger('app')


def safe_mkdir(p: str):
    try:
        os.mkdir(p)
        return 0
    except FileExistsError:
        return 1


def safe_mkdirs(p: str):
    try:
        os.makedirs(p)
        return 0
    except FileExistsError:
        return 1


class StartMenuDir:
    def __init__(self, path: str, type: str):
        self.path = path
        self.type = type
        self.is_accessible = self._check_on_accessible()

    def _check_on_accessible(self) -> bool:
        tmp_f = os.path.join(self.path, 'tmp.tmp')

        try:
            open(tmp_f, mode='w')
            os.remove(tmp_f)
        except WindowsError:
            return False

        return True

    def update_accessibility(self):
        self.is_accessible = self._check_on_accessible()


class SMObject(ABC):
    path: str
    name: str

    @abstractmethod
    def move(self, path_to_directory: str):
        ...

    @abstractmethod
    def delete(self):
        ...


class SMFolder(SMObject):
    name: str
    shortcuts: list['StartMenuShortcut']

    def is_empty(self):
        return len(self.shortcuts) == 0

    @staticmethod
    def _safe_file_move(src: str, dst_dir: str):
        try:
            os.rename(src, os.path.join(dst_dir, os.path.basename(src)))
        except FileExistsError:
            os.remove(src)

    def _recursion_move(self, dir_out: str, dir_in: str):
        """
        Move the shortcuts separately, not the entire folder as a whole. Otherwise,
        the built-in service shortcuts with translated names may not be displayed
        correctly.
        """
        for entry in os.scandir(dir_out):
            entry: os.DirEntry

            if entry.is_dir():
                new_dir_in = os.path.join(dir_in, entry.name)
                safe_mkdir(new_dir_in)
                self._recursion_move(entry.path, new_dir_in)
                continue

            self._safe_file_move(entry.path, dir_in)

    def move(self, path_to_directory: str):
        new_path = os.path.join(path_to_directory, self.name)
        safe_mkdir(new_path)
        self._recursion_move(self.path, new_path)
        self.delete()
        self.path = new_path

    def _safe_delete(self):
        os.rmdir(self.path)

    def delete(self):
        self._safe_delete()


class StartMenuFolder(SMFolder):
    def __init__(self, path: str, *, shortcuts: list['StartMenuShortcut'] = None):
        self.path: str = path
        self.name = os.path.basename(path)
        self.shortcuts = self._get_shortcuts() if not shortcuts else shortcuts

    def _get_shortcuts(self) -> list['StartMenuShortcut']:
        return [
            StartMenuShortcut(os.path.join(dir_data[0], sc))
            for dir_data in list(os.walk(self.path))
            for sc in dir_data[2] if os.path.splitext(sc)[-1] in ('.lnk', '.url')
        ]

    def update_shortcuts(self):
        self.shortcuts = self._get_shortcuts()

    def __repr__(self, indent: int = 4):
        indent_text = ' ' * indent
        # first \n need for correct display print(list[StartMenuFolder])
        return f'\n{self.name}\n' + '\n'.join(indent_text + shortcut.name for shortcut in self.shortcuts)

    def copy(self):
        return type(self)(self.path, shortcuts=self.shortcuts)


class StartMenuExtendedFolder(SMFolder):  # folder which exists in few start menu dirs
    def __init__(self, folders: list[SMFolder]):
        self.folders = []
        self.name = folders[0].name
        self.shortcuts = []

        for index, folder in enumerate(folders):
            if self.name != folder.name:
                raise ValueError('folders name must be same')

            self.shortcuts.extend(folder.shortcuts)

            if isinstance(folder, self.__class__):
                self.folders.extend(folder.folders)
            else:
                self.folders.append(folder)


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
        os.rename(self.path, new_p)
        self.path = new_p

    def relative_move(self, path_to_directory: str):
        new_path_to_dir = os.path.join(path_to_directory, os.path.split(self.get_rpath())[0])
        if not os.path.exists(new_path_to_dir):
            safe_mkdirs(new_path_to_dir)

        self.move(new_path_to_dir)

    def delete(self):
        os.remove(self.path)

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


class _CleanAction:
    MOVE = 0
    DELETE = 1

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
        return cls(cls.MOVE, 'move', {'path': path})

    @classmethod
    def delete(cls):
        return cls(cls.DELETE, 'delete')


@dataclass
class _FolderToClean:
    folder: SMFolder
    is_kept: bool
    shortcuts_to_apply: list[StartMenuShortcut]
    shortcuts_to_save: list[StartMenuShortcut]


class StartMenu:
    clean_action = _CleanAction
    folder_to_clean = _FolderToClean

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
    def update(cls):
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
    def clean(cls, action: _CleanAction, folders_to_clean: list[_FolderToClean]):
        LOG.info('=== START CLEAN ===')
        LOG.info(f'ACTION - <{action.name.upper()}>')

        cleaned_folders = applied_shortcuts = 0
        act_text = "moved" if action == cls.clean_action.MOVE else "deleted"

        for clean_f in folders_to_clean:
            log = lambda text: LOG.info(f'{clean_f.folder.name}: {text}')
            log(f'-- Folder start --')
            cleaned_folders += 1

            for clean_s in clean_f.shortcuts_to_apply:
                clean_s.relative_move(action.data['path']) if action == cls.clean_action.MOVE else clean_s.delete()
                applied_shortcuts += 1
                log(f'Shortcut "{clean_s.name}" was {act_text}')

            if clean_f.is_kept:
                log('Folder was kept')
                continue

            for saved_s in clean_f.shortcuts_to_save:
                saved_s.move(saved_s.get_fpath())  # move out
                log(f'Shortcut "{saved_s.name}" was moved out')

            if action == cls.clean_action.MOVE:
                clean_f.folder.move(action.data['path'])

            elif action == cls.clean_action.DELETE:
                clean_f.folder.delete()

            log(f'Folder was {act_text}')
            log(f'-- Folder end --')

        LOG.info(f'{cleaned_folders} folders were cleaned, {applied_shortcuts} shortcuts were {act_text}')
        LOG.info('=== END CLEAN ===')
        return cleaned_folders, applied_shortcuts
