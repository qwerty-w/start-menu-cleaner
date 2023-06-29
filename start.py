import argparse
import cleaner


parser = argparse.ArgumentParser('Start Menu Cleaner')
parser.add_argument(
    '--logging',
    help=f'full - recording full work in a single file, '
         f'cleaning - recording only the clean process to a file (each cleaning is a new file), '
         f'temp file path example - {cleaner.log.TempFilename("<name>", "<timestamp>").path}',
    choices=['full', 'cleaning'],
)
parser.add_argument(
    '--style',
    help='classic - default Windows style, '
         'material (by-default) - material style',
    choices=['classic', 'material'],
    default='material'
)


def main():
    args = parser.parse_args()
    style = getattr(cleaner.gui.Style, args.style.upper())
    if args.logging == 'full':
        cleaner.LOG.add_file_handler()
        cleaner.log.getLogger('cleaner.menu.clean').WRITE_LOG_FILE = False

    elif args.logging == 'cleaning':
        cleaner.log.getLogger('cleaner.menu.clean').KEEP_LOG_FILE = True

    cleaner.LOG.setLevel(cleaner.log.logging.INFO)
    cleaner.LOG.info(f'Application start ({style})')

    app = cleaner.widgets.QApplication([])
    app.setFont(cleaner.load_fonts('Roboto'))

    window = cleaner.MainWindow(app, style)

    cleaner.set_excepthook(app)

    cleaner.LOG.info('Show main window')
    window.show()
    cleaner.warn_inaccessible_dirs(window)

    app.exec()


if __name__ == '__main__':
    main()
