# Standard Library Imports
import json
import os

# Package imports
from .support import Base

# The addon profile directory
profile_dir = Base.get_info("profile")

__all__ = ["PersistentDict", "PersistentList", "PersistentSet"]


class BaseStorage(object):
    def __init__(self, filename, data_dir, updater, read_only):
        super(BaseStorage, self).__init__()
        self._filepath = os.path.join(data_dir, filename)
        self._stream = None

        # Load storage file if exists
        if os.path.exists(self._filepath):
            self._stream = file_obj = open(self._filepath, "rb" if read_only else "rb+")
            data = json.load(file_obj)
            updater(data)

        # Create missing data directory
        elif not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Disable sync if in read only mode
        if read_only:
            self.sync = object
            self.close()

    @property
    def _serialized(self):
        """
        Method to return back an serializable object.
        """
        return self

    def sync(self):
        """Syncrnize data to disk"""

        # Check if FileObj Needs Creating First
        if self._stream:
            self._stream.seek(0)
            self._stream.truncate(0)
        else:
            self._stream = open(self._filepath, "wb+")

        # Dumb data out to disk
        json.dump(self._serialized, self._stream, indent=4, separators=(",", ":"))
        self._stream.flush()

    def close(self, sync=False):
        """Synchronize and close file object."""
        if self._stream:
            if sync:
                self.sync()
            self._stream.close()
            self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class PersistentDict(BaseStorage, dict):
    """
    Persistence storage Dict that stores data on disk.

    Uses json for the backend.

    :param filename: Path to Persistence storage file.
    :type filename: str, unicode

    :param data_dir: (Optional) Directory where persistence storage file is located. (default => 'Profile Directory')
    :type data_dir: str, unicode

    :param read_only: (Optional) Open the file in ready only mode. (default => False)
    :type read_only: bool
    """
    def __init__(self, filename, data_dir=profile_dir, read_only=False):
        super(PersistentDict, self).__init__(filename, data_dir, self.update, read_only)


class PersistentList(BaseStorage, list):
    """
    Persistence storage List that stores data on disk.

    Uses json for the backend.

    :param filename: Path to Persistence storage file.
    :type filename: str, unicode

    :param data_dir: (Optional) Directory where persistence storage file is located. (default => 'Profile Directory')
    :type data_dir: str, unicode

    :param read_only: (Optional) Open the file in ready only mode. (default => False)
    :type read_only: bool
    """
    def __init__(self, filename, data_dir=profile_dir, read_only=False):
        super(PersistentList, self).__init__(filename, data_dir, self.extend, read_only)


class PersistentSet(BaseStorage, set):
    """
    Persistence storage Set that stores data on disk

    Uses json for the backend.

    :param filename: Path to Persistence storage file.
    :type filename: str, unicode

    :param data_dir: (Optional) Directory where persistence storage file is located. (default => 'Profile Directory')
    :type data_dir: str, unicode

    :param read_only: (Optional) Open the file in ready only mode. (default => False)
    :type read_only: bool
    """
    def __init__(self, filename, data_dir=profile_dir, read_only=False):
        super(PersistentSet, self).__init__(filename, data_dir, self.update, read_only)

    @property
    def _serialized(self):
        """Method to return a serializable object."""
        return list(self)
