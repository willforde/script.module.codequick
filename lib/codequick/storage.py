# -*- coding: utf-8 -*-

# Standard Library Imports
from hashlib import md5
import json
import os

# Package imports
from .support import Script

# The addon profile directory
profile_dir = Script.get_info("profile")


class PersistentDict(dict):
    """
    Persistent storage with a dictionary-like interface.

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
        super(PersistentDict, self).__init__()
        self._filepath = os.path.join(data_dir if data_dir else profile_dir, filename)
        self._stream = None
        self._hash = None

        # Load storage file if exists
        if os.path.exists(self._filepath):
            self._stream = file_obj = open(self._filepath, "rb" if read_only else "rb+")
            content = file_obj.read()

            # Calculate hash of file content
            self._hash = md5(content).hexdigest()

            # Load content and update storage
            data = json.loads(content)
            self.update(data)

        # Create missing data directory
        elif not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Disable sync if in read only mode
        if read_only:
            self.flush = object
            self.close()

    def flush(self):
        """Syncrnize data to disk"""

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
