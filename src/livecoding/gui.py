# coding=utf-8
import sys
import os
import signal
import argparse
import traceback

from PyQt5.QtCore import QTimer, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtQml import QQmlApplicationEngine

import livecoding
from livecoding import PythonReloader
from livecoding import recursively_register_types

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


class LiveCodingGui(QObject):
    def __init__(self, args, main_file, parent=None):
        super(LiveCodingGui, self).__init__(parent)
        sys.excepthook = self._display_error

        livecoding.register_types()

        qml_main = os.path.join(MODULE_PATH, 'live.qml')

        project_path = os.path.realpath(args.path)
        recursively_register_types(project_path)

        self._engine = QQmlApplicationEngine()
        self._engine.addImportPath(os.path.abspath('.'))
        self._engine.rootContext().setContextProperty('parsedArguments', vars(args))

        global reloader  # necessary to make reloading work, prevents garbage collection
        reloader = PythonReloader(main_file)
        self._engine.rootContext().setContextProperty(PythonReloader.__name__, reloader)
        self._engine.rootContext().setContextProperty('userProjectPath', project_path)

        self._engine.load(qml_main)

        self._start_check_timer()

    def _start_check_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(lambda: None)
        self._timer.start(100)

    @staticmethod
    def shutdown():
        QApplication.quit()

    @staticmethod
    def _display_error(etype, evalue, etraceback):
        tb = ''.join(traceback.format_exception(etype, evalue, etraceback))
        sys.stderr.write("FATAL ERROR: An unexpected error occurred:\n{}\n\n{}\n".format(evalue, tb))


def main(main_file):
    signal.signal(signal.SIGINT, lambda *args: LiveCodingGui.shutdown())

    parser = argparse.ArgumentParser(description="Live Coding GUI")
    parser.add_argument('path', help='Path where the live coding should be executed.', nargs='?', default='.')
    arguments, unknown = parser.parse_known_args()

    app = QApplication(sys.argv)
    app.setOrganizationName('Machine Koder')
    app.setOrganizationDomain('machinekoder.com')
    app.setApplicationName('Live Coding example')
    app.setWindowIcon(QIcon(os.path.join(MODULE_PATH, 'icon.png')))

    # noinspection PyUnusedLocal
    gui = LiveCodingGui(arguments, main_file)

    sys.exit(app.exec_())
