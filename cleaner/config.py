import os
import configparser


class Config(configparser.ConfigParser):
    def __init__(self):
        super().__init__({'lang': 'en', 'show_inaccessible_warn': 'true'}, default_section='opt')
        self.path = os.path.join(os.getenv('PROGRAMDATA'), 'SMCleaner', 'config.ini')

        if not os.path.exists(self.path):
            if not os.path.exists(dirs := os.path.dirname(self.path)):
                os.makedirs(dirs)

            self.update()
        else:
            with open(self.path) as f:
                self.read(f)

    def save(self):
        with open(self.path, 'w') as f:
            self.write(f)


CONFIG = Config()
