import logging

LOG = logging.getLogger('app')
LOG.addHandler(logging.StreamHandler())
LOG.handlers[-1].setFormatter(logging.Formatter('[{asctime}] {message}', '%H:%M:%S', '{'))

LOG.setLevel(logging.INFO)
