import os
import sys

from . import log
from .menu import StartMenu
from .gui import MainWindow, widgets, warn_inaccessible_dirs


LOG = log.getLogger(__name__)


def set_excepthook(app: gui.widgets.QApplication):
    def excepthook(cls, e, tb):
        LOG.critical('App error:', exc_info=(cls, e, tb))
        LOG.warning('App was closed by critical error')
        app.exit(1)
        sys.exit(1)

    sys.excepthook = excepthook
