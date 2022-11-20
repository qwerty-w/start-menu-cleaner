import os
from os import path
import struct

import icoextract


DEFAULT_START_MENU_OBJECTS_DIRS = [
    path.join(os.getenv('AppData'), r'Microsoft\Windows\Start Menu\Programs'),
    path.join(os.getenv('SystemDrive'), r'\ProgramData\Microsoft\Windows\Start Menu\Programs')
]


def get_shortcut_link(ph):
    with open(ph, 'rb') as stream:
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
        # skip 12 bytes (LinkInfoHeaderSize, LinkInfoFlags, and VolumeIDOffset)
        position += 0x0C
        # go to the LocalBasePath position
        lbpos = struct.unpack('I', content[position:position+0x04])[0]
        position = last_pos + lbpos
        # read the string at the given position of the determined length
        size= (length + last_pos) - position - 0x02
        temp = struct.unpack('c' * size, content[position:position+size])
        target = ''.join([chr(ord(a)) for a in temp])


def get_exe_icon(ph: str) -> bytes:
    return icoextract.IconExtractor(ph).get_icon().getvalue()


class StartMenuShortcut:
    def __init__(self, ph: str):
        self.path: str = ph
        self.name, self.ext = path.splitext(path.basename(ph))

    def __repr__(self):
        return self.path


class StartMenuFolder:
    def __init__(self, ph: str):
        self.path: str = ph
        self.name: str = path.basename(ph)
        self.shortcuts: list[StartMenuShortcut] = self.get_recursion_shortcuts()

    def get_recursion_shortcuts(self) -> list[StartMenuShortcut]:
        return [
            StartMenuShortcut(path.join(dir_data[0], sc)) for dir_data in list(os.walk(self.path)) for sc in dir_data[2]
        ]

    def __repr__(self, indent: int = 4):
        indent_text = ' ' * indent
        # first \n need for correct display print(list[StartMenuFolder])
        return f'\n{self.name}\n' + '\n'.join(indent_text + shortcut.name for shortcut in self.shortcuts)


class StartMenu:
    @staticmethod
    def get_folders():
        folders = []

        for sm_dir in DEFAULT_START_MENU_OBJECTS_DIRS:
            for item in os.listdir(sm_dir):
                full_path = path.join(sm_dir, item)

                if path.isdir(full_path):
                    folders.append(StartMenuFolder(ph=full_path))

        return folders
