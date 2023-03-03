import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


import logging
from .menu import StartMenu
from .gui import MainWindow, widgets, warn_inaccessible_dirs


LOG = logging.getLogger(__name__)
stream = logging.StreamHandler()
stream.setFormatter(logging.Formatter('[{asctime}] {message}', '%H:%M:%S', '{'))
LOG.addHandler(stream)
