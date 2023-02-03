import cleaner


def main():
    cleaner.LOG.info('Application start')
    app = cleaner.widgets.QApplication([])
    window = cleaner.MainWindow()

    cleaner.LOG.info('Show inaccessible start menu shortcuts dirs warning')
    cleaner.warn_inaccessible_dirs(window)

    window.show()
    cleaner.LOG.info('Show main window')
    app.exec()


if __name__ == '__main__':
    main()
