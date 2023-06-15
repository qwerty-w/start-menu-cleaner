import argparse
import cleaner


parse = argparse.ArgumentParser('Start Menu Cleaner')
parse.add_argument(
    '--logging',
    help=f'full - recording full work in a single file, '
         f'cleaning - recording only the clean process to a file (each cleaning is a new file), '
         f'temp file path example - {cleaner.log.TempFilename("<name>", "<timestamp>").path}',
    choices=['full', 'cleaning']
)


def main():
    args = parse.parse_args()

    if args.logging == 'full':
        cleaner.LOG.add_file_handler()
        cleaner.log.getLogger('cleaner.menu.clean').WRITE_LOG_FILE = False

    elif args.logging == 'cleaning':
        cleaner.log.getLogger('cleaner.menu.clean').KEEP_LOG_FILE = True

    cleaner.LOG.setLevel(cleaner.log.logging.INFO)
    cleaner.LOG.info('Application start')
    app = cleaner.widgets.QApplication([])
    window = cleaner.MainWindow()

    cleaner.set_excepthook(app)
    cleaner.warn_inaccessible_dirs(window)

    window.show()
    cleaner.LOG.info('Show main window')
    app.exec()


if __name__ == '__main__':
    main()
