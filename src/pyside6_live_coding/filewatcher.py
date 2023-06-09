import os
from fnmatch import fnmatch

from PySide6.QtCore import (
    QObject,
    Property,
    Signal,
    QFileSystemWatcher,
    QUrl,
    QDirIterator,
    qWarning,
)


class FileWatcher(QObject):

    fileUrlChanged = Signal(QUrl)
    enabledChanged = Signal(bool)
    recursiveChanged = Signal(bool)
    nameFiltersChanged = Signal('QStringList')
    fileChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._file_url = QUrl()
        self._enabled = True
        self._recursive = False
        self._name_filters = []
        self._watched_paths = set()

        self._file_system_watcher = QFileSystemWatcher()

        self.fileUrlChanged.connect(self._update_watched_file)
        self.enabledChanged.connect(self._update_watched_file)
        self.recursiveChanged.connect(self._update_watched_file)
        self.nameFiltersChanged.connect(self._update_watched_file)
        self._file_system_watcher.fileChanged.connect(
            self._on_watched_file_changed
        )
        self._file_system_watcher.directoryChanged.connect(
            self._on_watched_directory_changed
        )

    @Property(QUrl, notify=fileUrlChanged)
    def fileUrl(self):
        return self._file_url

    @fileUrl.setter
    def fileUrl(self, value):
        if self._file_url == value:
            return
        self._file_url = value
        self.fileUrlChanged.emit(value)

    @Property(bool, notify=enabledChanged)
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled == value:
            return
        self._enabled = value
        self.enabledChanged.emit(value)

    @Property(bool, notify=recursiveChanged)
    def recursive(self):
        return self._recursive

    @recursive.setter
    def recursive(self, value):
        if self._recursive == value:
            return
        self._recursive = value
        self.recursiveChanged.emit(value)

    @Property('QStringList', notify=nameFiltersChanged)
    def nameFilters(self):
        return self._name_filters

    @nameFilters.setter
    def nameFilters(self, value):
        if (
            self._name_filters == value
        ):  # note: we compare the reference here, not the actual list
            return
        self._name_filters = value
        self.nameFiltersChanged.emit(value)

    def _update_watched_file(self):
        if files := self._file_system_watcher.files():
            self._file_system_watcher.removePaths(files)
        if directories := self._file_system_watcher.directories():
            self._file_system_watcher.removePaths(directories)

        if not self._file_url.isValid() or not self._enabled:
            return False

        if not self._file_url.isLocalFile():
            qWarning('Can only watch local files')
            return False

        local_file = self._file_url.toLocalFile()
        if local_file == '':
            return False

        if os.path.isdir(local_file):
            changed, self._watched_paths = self._update_watched_directory(
                local_file, self._watched_paths
            )
            return changed

        elif os.path.exists(local_file):
            self._file_system_watcher.addPath(local_file)
            return True

        else:
            qWarning('File to watch does not exist')
            return False

    def _update_watched_directory(self, local_file, watched_paths):
        new_paths = {local_file}
        self._file_system_watcher.addPath(local_file)

        options = QDirIterator.FollowSymlinks
        if self._recursive:
            options |= QDirIterator.Subdirectories
        it = QDirIterator(local_file, options)
        while it.hasNext():
            filepath = it.next()
            filename = os.path.basename(filepath)
            filtered = any(
                fnmatch(filename, wildcard) for wildcard in self._name_filters
            )
            if filename == '..' or filename == '.' or filtered:
                continue
            self._file_system_watcher.addPath(filepath)
            new_paths.add(filepath)

        return new_paths != watched_paths, new_paths

    def _on_watched_file_changed(self):
        if self._enabled:
            self.fileChanged.emit()

    def _on_watched_directory_changed(self, _):
        if self._update_watched_file():
            self._on_watched_file_changed()
