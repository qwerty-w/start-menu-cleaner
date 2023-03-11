import argparse
import cleaner


parse = argparse.ArgumentParser('Start Menu Cleaner')
parse.add_argument(
    '--log-clean',
    action=argparse.BooleanOptionalAction,
    help='',
    default=False,
)


def main():
    cleaner.LOG.setLevel(cleaner.logging.INFO)

    args = parse.parse_args()
    if args.log_clean:
        cleaner.menu.SMCleaner.LOG.KEEP_LOG_FILE = True

    cleaner.LOG.info('Application start')
    app = cleaner.widgets.QApplication([])
    window = cleaner.MainWindow()

    cleaner.warn_inaccessible_dirs(window)

    window.show()
    cleaner.LOG.info('Show main window')
    app.exec()


if __name__ == '__main__':
    main()
