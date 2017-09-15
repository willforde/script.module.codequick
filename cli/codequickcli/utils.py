# Standard Library Imports
import unicodedata
import hashlib
import sys
import re

try:
    import urllib.parse as urlparse
except ImportError:
    # noinspection PyUnresolvedReferences
    import urlparse

try:
    # noinspection PyUnresolvedReferences
    long_type = long
except NameError:
    long_type = int

try:
    # noinspection PyUnresolvedReferences
    input_raw = raw_input
except NameError:
    input_raw = input

PY3 = sys.version_info >= (3, 0)
# Unicode Type object, unicode on python2 or str on python3
unicode_type = type(u"")


class CacheProperty(object):
    """
    Converts a class method into a property.

    When property is accessed for the first time, the result is computed and returned.
    The class property is then replaced with an instance attribute with the computed result.
    """

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self._func = func

    def __get__(self, instance, owner):
        if instance:
            attr = self._func(instance)
            setattr(instance, self.__name__, attr)
            return attr
        else:
            return self


def safe_path(path, encoding="utf8"):
    """
    Convert path into a encoding that best suits the platform os.
    Unicode when on windows, utf8 when on linux/bsd.

    :type path: bytes or unicode
    :param path: The path to convert.
    :param encoding: The encoding to use when needed.
    :return: Returns the path as unicode or utf8 encoded string.
    """
    return ensure_unicode(path, encoding) if sys.platform.startswith("win") else ensure_bytes(path, encoding)


def ensure_bytes(data, encoding="utf8"):
    """
    Ensures that given string is returned as a UTF-8 encoded string.

    :param data: String to convert if needed.
    :param encoding: The encoding to use when encoding.
    :returns: The given string as UTF-8.
    :rtype: bytes
    """
    return data if isinstance(data, bytes) else unicode_type(data).encode(encoding)


def ensure_native_str(data, encoding="utf8"):
    """
    Ensures that given string is returned as a native str type, bytes on python2 or unicode on python3.

    :param data: String to convert if needed.
    :param encoding: The encoding to use when encoding.
    :returns: The given string as UTF-8.
    :rtype: str
    """
    if isinstance(data, str):
        return data
    elif isinstance(data, unicode_type):
        # Only executes on python 2
        return data.encode(encoding)
    elif isinstance(data, bytes):
        # Only executes on python 3
        return data.decode(encoding)
    else:
        str(data)


def ensure_unicode(data, encoding="utf8"):
    """
    Ensures that given string is return as a unicode string.

    :param data: String to convert if needed.
    :param encoding: The encoding to use when decoding.
    :returns: The given string as unicode.
    :rtype: unicode
    """
    return data.decode(encoding) if isinstance(data, bytes) else unicode_type(data)


# Used by xbmc.makeLegalFilename
def normalize_filename(filename):
    """
    Returns a legal filename or path as a string.

    :param filename:
    :type filename: str or unicode

    :return: Legal filename or path as a string
    :rtype: str
    """
    value = unicodedata.normalize('NFKD', ensure_unicode(filename)).encode("ascii", "ignore").decode("ascii")
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return ensure_native_str(value)


# Used by xbmcgui.Dialog.input
def hash_password(password):
    """
    Hash a giving password using md5 and return the hash value.

    :param str password: The password to hash
    :returns: The password as a md5 hash
    :rtype: str
    """
    return hashlib.md5(password).hexdigest()
