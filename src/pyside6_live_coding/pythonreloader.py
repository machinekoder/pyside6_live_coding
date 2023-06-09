import os
import sys
import signal
import inspect

from PySide6.QtCore import QObject, Slot


class PythonReloader(QObject):
    def __init__(self, main, parent=None):
        super(PythonReloader, self).__init__(parent)
        self._main = main

    @Slot()
    def restart(self):
        import_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
        python_path = os.environ.get('PYTHONPATH', '')
        if import_dir not in python_path:
            python_path += f':{import_dir}'
        os.environ['PYTHONPATH'] = python_path
        args = [sys.executable, self._main] + sys.argv[1:]
        if handler := signal.getsignal(signal.SIGTERM):
            handler(signal.SIGTERM, inspect.currentframe())
        os.execv(sys.executable, args)
