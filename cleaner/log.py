import os
import time
import tempfile
import logging
from typing import Optional


# noinspection PyUnresolvedReferences, PyPep8Naming, PyTypeHints
def _getLogger(name: str) -> logging.Logger:
    manager = logging.Logger.manager
    obj = manager.loggerDict.get(name)
    custom_loggers = {
        'cleaner': AppLogger,
        'cleaner.menu.clean': CleanLogger
    }

    if not custom_loggers.get(name) or isinstance(obj, custom_loggers[name]):
        logger = logging.getLogger(name)

    else:
        # wrap logger as logging.getLogger
        logger = custom_loggers[name](name)
        logger.manager = manager

        if isinstance(obj, logging.PlaceHolder):
            manager._fixupChildren(obj, logger)

        manager.loggerDict[name] = logger
        manager._fixupParents(logger)

    return logger


# noinspection PyUnresolvedReferences, PyPep8Naming
def getLogger(name: str) -> logging.Logger:
    logging._acquireLock()
    try:
        return _getLogger(name)
    finally:
        logging._releaseLock()


class TempFilename:
    def __init__(self, name: str, timestamp: str = None):
        timestamp = timestamp if timestamp is not None else str(int(time.time()))
        self.name = f'sm-{name}-{timestamp}.log'
        self.path = os.path.join(tempfile.gettempdir(), self.name)


class MainFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__('[%(asctime)s] %(label)s%(message)s', '%H:%M:%S', *args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        folder, shortcut = (record.__dict__.pop(n, None) for n in ['folder_name', 'shortcut_name'])
        record.label = f'{folder}:{shortcut} -> ' if folder and shortcut else f'{folder} -> ' if folder else ''
        return super().format(record)


class AppLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)

        s_handler = logging.StreamHandler()
        s_handler.setFormatter(MainFormatter())
        self.addHandler(s_handler)

    @staticmethod
    def get_tmp_fn(*, timestamp: str = None):
        return TempFilename('app', timestamp)

    def add_file_handler(self):
        f_handler = logging.FileHandler(self.get_tmp_fn().path)
        f_handler.setFormatter(MainFormatter())
        self.addHandler(f_handler)


class CleanLogger(logging.Logger):
    """
    todo: ...
    """

    def __init__(self, name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        self.file: Optional[logging.FileHandler] = None
        self.propagate = True  # explicitly

        self.WRITE_LOG_FILE = True
        self.KEEP_LOG_FILE = False

    @staticmethod
    def get_tmp_fn(*, timestamp: str = None):
        return TempFilename('clean', timestamp)

    def init_file(self) -> None:
        if not self.WRITE_LOG_FILE:
            return

        fn = self.get_tmp_fn()
        self.file = logging.FileHandler(fn.path)
        self.file.setFormatter(MainFormatter())
        self.addHandler(self.file)

        self.info(f'Create .log file (by clean-init): {fn.name}')

    def reset_file(self, *, keep_file: bool = True, keep_reason: str = 'default') -> None:
        if not self.file:
            return

        f_name = os.path.basename(self.file.baseFilename)
        msg = '{} .log file (by clean-{}): ' + f_name

        if self.KEEP_LOG_FILE:
            self.info(msg.format('Keep', 'KEEP_LOG_FILE'))

        elif keep_file:
            self.info(msg.format('Keep', keep_reason))

        self.removeHandler(self.file)
        self.file.close()

        if not self.KEEP_LOG_FILE and not keep_file:
            os.remove(self.file.baseFilename)
            self.info(msg.format('Delete', 'reset'))

        self.file = None
