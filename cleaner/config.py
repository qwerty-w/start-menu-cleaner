import os
import configparser

from .log import getLogger


LOG = getLogger(__name__)


class Config(configparser.ConfigParser):
    def __init__(self):
        super().__init__({'lang': 'en', 'warn_inaccessible_dirs': 'true'}, default_section='opt')
        self.path = os.path.join(os.getenv('PROGRAMDATA'), 'SMCleaner', 'config.ini')

        if not os.path.exists(self.path):
            if not os.path.exists(dirs := os.path.dirname(self.path)):
                os.makedirs(dirs)

            self.save()
        else:
            self.read(self.path)

        LOG.info('Init config.ini')

    def save(self):
        with open(self.path, 'w') as f:
            self.write(f)

        LOG.debug(f'Save config / [opt]: {self.items("opt")}')


CONFIG = Config()
