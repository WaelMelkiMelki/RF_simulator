"""Desktop launcher. Use --check for diagnostics without a graphics context."""
import argparse
import importlib
import logging
import os
import sys


def check_dependencies():
    missing = []
    for name in ('PyQt6.QtWidgets', 'pyvista', 'pyvistaqt', 'qtpy', 'numpy', 'matplotlib', 'fpdf'):
        try:
            importlib.import_module(name)
        except (ImportError, OSError) as exc:
            missing.append(f'{name}: {exc}')
    if missing:
        print('\n'.join(missing), file=sys.stderr)
        print('No packages were installed. See README.md for existing-environment and offline options.', file=sys.stderr)
    return not missing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check imports without opening a window')
    args = parser.parse_args(argv)
    os.environ.setdefault('QT_API', 'pyqt6')
    logging.basicConfig(level=logging.INFO)
    if not check_dependencies():
        return 1
    try:
        from gui.main_window import MainWindow
        if args.check:
            print('Dependencies and MainWindow imports OK (rendering not tested).')
            return 0
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv[:1])
        app.setApplicationName('RF Simulator 3D')
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception:
        logging.exception('Application startup failed')
        return 1


if __name__ == '__main__':
    sys.exit(main())
