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


LOG = logging.getLogger('app')
LOG.addHandler(logging.StreamHandler())
LOG.handlers[-1].setFormatter(logging.Formatter('[{asctime}] {message}', '%H:%M:%S', '{'))

LOG.setLevel(logging.INFO)
