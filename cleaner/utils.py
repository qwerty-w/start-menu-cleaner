import os
from send2trash import send2trash


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


def rmove_dir(current_path: str, new_path: str, *, replace: bool = True):  # recursion move
    """
    Move the shortcuts separately, not the entire folder as a whole.
    """
    for entry in os.scandir(current_path):
        entry: os.DirEntry

        if entry.is_dir():
            subfolder_new_p = os.path.join(new_path, entry.name)
            if not os.path.exists(subfolder_new_p):
                safe_mkdir(subfolder_new_p)
            rmove_dir(entry.path, subfolder_new_p)

        else:
            file_new_p = os.path.join(new_path, os.path.basename(entry.path))

            if replace:
                os.replace(entry.path, file_new_p)

            elif not os.path.exists(file_new_p):
                os.rename(entry.path, file_new_p)

            else:  # if file exists and os.replace forbidden
                pass  # todo: maybe send2trash(entry.path)

    send2trash(current_path)


def recursion_rmdir(path: str):
    for entry in os.scandir(path):
        entry: os.DirEntry

        if entry.is_dir():
            recursion_rmdir(entry.path)

        else:
            os.remove(entry.path)

    os.rmdir(path)
