import logging

from .menu import StartMenu
from .gui import MainWindow, widgets, warn_inaccessible_dirs


LOG = logging.getLogger('app')
LOG.addHandler(logging.StreamHandler())
LOG.handlers[-1].setFormatter(logging.Formatter('[{asctime}] {message}', '%H:%M:%S', '{'))

LOG.setLevel(logging.INFO)
