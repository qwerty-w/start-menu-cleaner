import os


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


def rmove_dir(path: str, dir_in: str):  # recursion move
    """
    Move the shortcuts separately, not the entire folder as a whole. Otherwise,
    the built-in service shortcuts with translated names may not be displayed
    correctly.
    """
    for entry in os.scandir(path):
        entry: os.DirEntry

        if entry.is_dir():
            new_dir_in = os.path.join(dir_in, entry.name)
            safe_mkdir(new_dir_in)
            rmove_dir(entry.path, new_dir_in)

        else:
            os.replace(entry.path, os.path.join(dir_in, os.path.basename(entry.path)))

    os.rmdir(path)
