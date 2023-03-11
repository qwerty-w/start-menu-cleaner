import os
import sys
import logging
from .menu import StartMenu
from .gui import MainWindow, widgets, warn_inaccessible_dirs


LOG = logging.getLogger(__name__)
stream = logging.StreamHandler()
stream.setFormatter(logging.Formatter('[{asctime}] {message}', '%H:%M:%S', '{'))
LOG.addHandler(stream)
