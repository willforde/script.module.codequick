# -*- coding: utf-8 -*-

# Standard Library Imports
from hashlib import md5
import json
import sys
import os

# Package imports
from .base import Script

# The addon profile directory
profile_dir = Script.get_info("profile")


class _PersistentBase(object):
    """
    Base class to handle persistent file handling.

    :param filename: Filename of persistence storage file.
    :type filename: str or unicode

    :param data_dir: (Optional) Directory where persistence storage file is located. Defaults to profile directory.
    :type data_dir: str or unicode

    :param read_only: (Optional) Open the file in read only mode, Disables writeback. (default => False)
    :type read_only: bool
    """
    def __init__(self, filename, data_dir=None, read_only=False):
        super(_PersistentBase, self).__init__()
        self._read_only = read_only
        self._stream = None
        self._hash = None

        # Ensure that filepath is either all bytes or unicode depending on platform type, windows, linux or bsd.
        data_dir = (data_dir.decode("utf8") if isinstance(data_dir, bytes) else data_dir) if data_dir else profile_dir
        self._filepath = os.path.join(data_dir, filename.decode("utf8") if isinstance(filename, bytes) else filename)
        if not sys.platform.startswith("win"):
            self._filepath = self._filepath.encode("utf8")

        # Create any missing data directory
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load(self):
        """Load in existing data from disk."""
        # Load storage file if exists
        if os.path.exists(self._filepath):
            if self._read_only:
                file_obj = open(self._filepath, "rb")
                content = file_obj.read()
                file_obj.close()
            else:
                self._stream = file_obj = open(self._filepath, "rb+")
                content = file_obj.read()

            # Calculate hash of file content
            self._hash = md5(content).hexdigest()

            # Load content and update storage
            return json.loads(content)

    def flush(self):
        """Syncrnize data to disk."""
        if self._read_only:
            return None

        # Serialize the storage data
        content = json.dumps(self, indent=4, separators=(",", ":"))
        current_hash = md5(content).hexdigest()

        # Compare saved hash with current hash, to detect if content has changed
        if self._hash is None or self._hash != current_hash:
            # Check if FileObj Needs Creating First
            if self._stream:
                self._stream.seek(0)
                self._stream.truncate(0)
            else:
                self._stream = open(self._filepath, "wb+")

            # Dump data out to disk
            self._stream.write(content)
            self._hash = current_hash
            self._stream.flush()

    def close(self):
        """Synchronize and close file object."""
        self.flush()
        if self._stream:
            self._stream.close()
            self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class PersistentDict(_PersistentBase, dict):
    """
    Persistent storage with a dictionary interface.

    It is designed as a context manager.
    Uses json for the backend.

    .. note:: Sense json is used as the backend, all objects within this dict, must be json serializable.

    :param filename: Filename of persistence storage file.
    :type filename: str or unicode

    :param data_dir: (Optional) Directory where persistence storage file is located. Defaults to profile directory.
    :type data_dir: str or unicode

    :param read_only: (Optional) Open the file in read only mode, Disables writeback. (default => False)
    :type read_only: bool
    """

    def __init__(self, filename, data_dir=None, read_only=False):
        super(PersistentDict, self).__init__(filename, data_dir, read_only)
        current_data = self._load()
        if current_data:
            self.update(current_data)


class PersistentList(_PersistentBase, list):
    """
    Persistent storage with a list interface.

    It is designed as a context manager.
    Uses json for the backend.

    .. note:: Sense json is used as the backend, all objects within this dict, must be json serializable.

    :param filename: Filename of persistence storage file.
    :type filename: str or unicode

    :param data_dir: (Optional) Directory where persistence storage file is located. Defaults to profile directory.
    :type data_dir: str or unicode

    :param read_only: (Optional) Open the file in read only mode, Disables writeback. (default => False)
    :type read_only: bool
    """

    def __init__(self, filename, data_dir=None, read_only=False):
        super(PersistentList, self).__init__(filename, data_dir, read_only)
        current_data = self._load()
        if current_data:
            self.extend(current_data)
