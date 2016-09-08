# Standard Library Imports
from shelve import DbfilenameShelf
import json
import os


__all__ = ["DictStorage", "ListStorage", "SetStorage", "ShelfStorage"]


def unicode_converter(func):
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
    _filename = u"metadata.json"

    def __del__(self):
        """ Close connection to file object if not already closed """
        if not self.closed:
            self.close()

    def __init__(self, data_dir, filename=None):
        self.closed = False
        if not filename:
            filename = self._filename

        filepath = os.path.join(data_dir, filename)
        self._filepath = filepath

        # Load Store Dict from Disk if Available
        if os.path.exists(filepath):
            self._fileObj = open(filepath, "rb+")
            self._load()
        else:
            self._fileObj = None
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

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
            self._fileObj = open(self._filepath, "wb+")

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
    _filename = u"metadata_dict.json"


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
    _filename = u"metadata_list.json"

    def update(self, args):
        """ Helper method to allow use of add on storage object to extend list """
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
    _filename = u"metadata_set.json"

    def serialize(self):
        """
        Override method to return a list version of the Set object
        that can be easily serialize
        """
        return list(self)


class ShelfStorage(DbfilenameShelf):
    """
    Persistence storage that is a subclass of shelf that stores data on disk

    Preferred over dict_storage when dealing with a large amounts
    of data. sense only the required data is read in from disk instead
    of the whole file and only the data thats added to object is written to file

    Parameters
    ----------
    filename : unicode
        Path for the underlying database

    flag : str, optional(default='c')
        The optional flag argument must be one of these values:

        'r' 	Open existing database for reading only (default)
        'w' 	Open existing database for reading and writing
        'c' 	Open database for reading and writing, creating it if it doesn't exist
        'n' 	Always create a new, empty database, open for reading and writing

    protocol, int, optional(default=pickle.HIGHEST_PROTOCOL)
        The version of the pickle protocol serializing the data


    writeback: bool, optional(default=True)
        Because of Python semantics, a shelf cannot know when a mutable persistent-dictionary entry is modified.
        By default modified objects are written only when assigned to the shelf. If the optional writeback parameter
        is set to True, all entries accessed are also cached in memory, and written back on sync() and close().

    Methods
    -------
    All of the methods that are available to the Shelf object
    """

    def __init__(self, data_dir, filename=u"metadata_dict.shelf", protocol=-1, writeback=False):
        filepath = os.path.join(data_dir, filename)
        DbfilenameShelf.__init__(self, filepath, protocol=protocol, writeback=writeback)

    @unicode_converter
    def __getitem__(self, key):
        return DbfilenameShelf.__getitem__(self, key)

    @unicode_converter
    def __setitem__(self, key, value):
        DbfilenameShelf.__setitem__(self, key, value)

    @unicode_converter
    def __delitem__(self, key):
        DbfilenameShelf.__delitem__(self, key)

    @unicode_converter
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
