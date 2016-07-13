# Standard Library Imports
from shelve import DbfilenameShelf
import os
import json

__all__ = ["DictStorage", "ListStorage", "SetStorage"]


def _unicode_handler(func):
    """
    Decorate to make sure that the key is always str object and not a unicode object.

    Note
    ----
    This is used for Shelf storage because the shelve modual cant handle unicode keys

    Parameters
    ----------
    func
        Fuction to decorate
    """
    def wrapper(self, key, *args):
        if isinstance(key, unicode):
            return func(self, str(key), *args)
        else:
            return func(self, key, *args)

    return wrapper


class _BaseStorage(object):
    def __del__(self):
        """ Close connection to file object if not already closed """
        if not self.closed:
            self.close()

    def __init__(self, filename):
        # Load and set serializer object
        self._filename = filename
        self.closed = False

        # Load Store Dict from Disk if Available
        if os.path.exists(filename):
            self._fileObj = open(filename, "rb+")
            self._load()
        else:
            self._fileObj = None
            dirpath = os.path.dirname(filename)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

    def serialize(self):
        """
        Method to return back an object that can be serialize.
        Can be overridden by sub classes to support object that cant be easily deserialize
        """
        return self

    def _load(self):
        # Load Data from Disk
        self._fileObj.seek(0)
        self.update(json.load(self._fileObj))

    def sync(self):
        """ Syncrnize data to disk """

        # Check if FileObj Needs Creating First
        if self._fileObj:
            self._fileObj.seek(0)
            self._fileObj.truncate(0)
        else:
            self._fileObj = open(self._filename, "wb+")

        # Dumb Data to Disk
        json.dump(self.serialize(), self._fileObj, indent=4, separators=(",", ":"))

        # Flush Data out to Disk
        self._fileObj.flush()

    def close(self, sync=False):
        """
        Close connection to file object

        Parameters
        ----------
        sync : bool, optional(default=False)
            Syncrnize data to disk before closing file.
        """
        if sync:
            self.sync()

        if self._fileObj and not self.closed:
            self._fileObj.close()

        self.closed = True

    # Methods to add support for with statement
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class DictStorage(_BaseStorage, dict):
    """
    Persistence storage Dict that stores data on disk

    Parameters
    ----------
    filename : unicode
        Path to Persistence storage file.

    Works by using json to load all the contents of the file into memory.
    May be slow when working with a lot of data, also not very memory efficient.
    Though can be quite fast when dealing with smaller amounts of data and doing more reads
    than writes sense writes are slow due to having to write all the contents of the file back to disk.
    shelf_storage is Preferred when working with a lot of data.

    Methods:
    All of the methods that are available to the Dictionary object
    sync() : Used to synchronized the in memory object with the on disk file
    close(True) : Synchronize data if required and close connection of opened file
    """

    pass


class ListStorage(_BaseStorage, list):
    """
    Persistence storage List that stores data on disk

    Parameters
    ----------
    filename : unicode
        Path to Persistence storage file.

    Works by using json to load all the contents of the file into memory.
    May be slow when working with a lot of data, also not very memory efficient.
    Though can be quite fast when dealing with smaller amounts of data and doing more reads
    than writes sense writes are slow due to having to write all the contents of the file back to disk.

    Methods:
    All of the methods that are available to the list object
    sync() : Used to synchronized the in memory object with the on disk file
    close(True) : Synchronize data if required and close connection of opened file
    """

    def update(self, args):
        """ Helper method to allow use of update on storage object to extend list """
        self.extend(args)


class SetStorage(_BaseStorage, set):
    """
    Persistence storage Set that stores data on disk

    Parameters
    ----------
    filename : unicode
        Path to Persistence storage file.

    Works by using json to load all the contents of the file into memory.
    May be slow when working with a lot of data, also not very memory efficient.
    Though can be quite fast when dealing with smaller amounts of data and doing more reads
    than writes sense writes are slow due to having to write all the contents of the file back to disk.

    Methods
    -------
    All of the methods that are available to the Set object
    sync() : Used to synchronized the in memory object with the on disk file
    close(True) : Synchronize data if required and close connection of opened file
    """

    def serialize(self):
        """
        Override method to return a list version of the Set object
        that can be easily serialize
        """
        return list(self)


class ShelfStorage(DbfilenameShelf):
    """
    Persistence storage Shelf that stores data on disk

    Same parameters as shelve.open(filename, flag='c', protocol=None, writeback=False)

    Preferred over dict_storage when dealing with a large amounts
    of data. sense only the required data is read in from disk instead
    of the whole file and only the data thats added to object is written to file

    Methods
    -------
    All of the methods that are available to the Shelf object
    """

    @_unicode_handler
    def __getitem__(self, key):
        return DbfilenameShelf.__getitem__(self, key)

    @_unicode_handler
    def __setitem__(self, key, value):
        DbfilenameShelf.__setitem__(self, key, value)

    @_unicode_handler
    def __delitem__(self, key):
        DbfilenameShelf.__delitem__(self, key)

    @_unicode_handler
    def __contains__(self, key):
        return key in self.dict

    def get(self, key, default=None):
        """ Return the value for a given key if key is in the database, will return default if not. """
        try:
            value = self[key]
        except KeyError:
            return default
        else:
            return value

    def keys(self):
        """ Return a list of all the key in the database

        Returns
        -------
        list of str
        """
        return [unicode(key) if isinstance(key, str) else key for key in self.dict]
