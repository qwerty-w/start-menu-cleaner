import os
import struct
import locale
from typing import Union


DEFAULT_START_MENU_SHORTCUTS_DIRS = [
    os.path.join(os.getenv('AppData'), r'Microsoft\Windows\Start Menu\Programs'),
    os.path.join(os.getenv('SystemDrive'), r'\ProgramData\Microsoft\Windows\Start Menu\Programs')
]


class StartMenuShortcut:
    def __init__(self, ph: str):
        self.path: str = ph
        self.name, self.ext = os.path.splitext(os.path.basename(ph))

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

    def __repr__(self):
        return self.path


class SMFolder:
    shortcuts: list

    def is_empty(self):
        return len(self.shortcuts) == 0


class StartMenuFolder(SMFolder):
    def __init__(self, path: str, *, shortcuts: list[StartMenuShortcut] = None):
        self.path: str = path
        self.name: str = os.path.basename(path)
        self.shortcuts: list[StartMenuShortcut] = self.get_recursion_shortcuts() if not shortcuts else shortcuts

    def get_recursion_shortcuts(self) -> list[StartMenuShortcut]:
        return [
            StartMenuShortcut(os.path.join(dir_data[0], sc))
            for dir_data in list(os.walk(self.path))
            for sc in dir_data[2] if os.path.splitext(sc)[-1] in ('.lnk', '.url')
        ]

    def __repr__(self, indent: int = 4):
        indent_text = ' ' * indent
        # first \n need for correct display print(list[StartMenuFolder])
        return f'\n{self.name}\n' + '\n'.join(indent_text + shortcut.name for shortcut in self.shortcuts)

    def copy(self):
        return type(self)(self.path, shortcuts=self.shortcuts)


class StartMenuExtendedFolder(SMFolder):
    def __init__(self, folders: list[Union[StartMenuFolder, 'StartMenuExtendedFolder']]):
        self.folders = []
        self.name = folders[0].name
        self.shortcuts = []

        for index, folder in enumerate(folders):
            if self.name != folder.name:
                raise ValueError('folders name must be same')

            if isinstance(folder, self.__class__):
                self.folders.extend(folder.folders)
                continue

            self.folders.append(folder)
            self.shortcuts.extend(folder.shortcuts)


class StartMenu:
    @staticmethod
    def get_folders() -> list[Union[StartMenuFolder, StartMenuExtendedFolder]]:
        folders = []

        for sm_dir in DEFAULT_START_MENU_SHORTCUTS_DIRS:
            for item in os.listdir(sm_dir):
                full_path = os.path.join(sm_dir, item)

                if not os.path.isdir(full_path):
                    continue

                new_folder = StartMenuFolder(path=full_path)
                for index, folder in enumerate(folders):
                    if folder.name == new_folder.name:
                        folders[index:index + 1] = [StartMenuExtendedFolder([folder, new_folder])]
                        break

                else:
                    folders.append(new_folder)

        folders.sort(key=lambda x: x.name.lower())
        return folders
