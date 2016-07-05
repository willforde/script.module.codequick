# Standard Library Imports
import collections
import urlparse
import logging
import urllib
import time
import sys
import os

# Kodi Imports
import xbmcplugin
import xbmcaddon
import xbmcgui
import xbmc


def translate_path(path):
    """ Returns the translated path as unicode """
    if path[:10] == "special://":
        return unicode(xbmc.translatePath(path), "utf8")
    else:
        return unicode(path, "utf8")


def cls_for_route(route_path, raise_on_error=False):
    """
    Return class thats associated with specified route

    route : string or unicode --- Route thats associated with a class
    [raise_on_error] : Boolean --- State if a KeyError will be raised if no class was found for specified route.
    """
    route_path = str(route_path)
    for cls, pattern in _routes.iteritems():
        if pattern == route_path.lower():
            return cls
    else:
        # No available class matching specified route was found
        if raise_on_error:
            raise KeyError("No class for route: %s" % route_path)
        else:
            return None


def localized(strings):
    """
    Add dict of localized string / id pairs to get_local_string

    strings : dict --- String/id pairs to allow accessing localized strings using string value instead of id
    """
    _strings.update(strings)


def route(route_pattern):
    """
    Decorator to bind a class to a route that can be called via route dispatcher.

    Args:
        route_pattern (str|unicode): The route that will point to the bind class

    Returns:
        object: Decorated class
    """
    route_pattern = str(route_pattern.lower())

    def decorator(cls):
        _routes[cls] = route_pattern
        cls._route = route_pattern
        return cls

    return decorator


def run(buggalo_email=None, debug=False, error_time=10000):
    """
    Call Class instance thats associated with route passed in from kodi sys args.

    debug: boolean --- if True then show debug messages in log without kodi debug mode been enabled. (default False)
    :rtype: object
    """

    # Set logger debug mode
    before = time.time()

    try:
        # Check if running as plugin or script
        argv = sys.argv
        if argv[0][:9] == "plugin://":
            url = argv[0] + argv[2]
        else:
            arg_len = len(argv)
            if arg_len == 1:
                raise ValueError("No action value was giving from script call")
            elif arg_len == 2:
                url = "plugin://%s/%s" % (str(addonID), argv[1])
            else:
                query = "&".join(["arg%i=%s" % (count, arg) for count, arg in enumerate(argv[2:], start=1)])
                url = "plugin://%s/%s?%s" % (str(addonID), sys.argv[1], query)

        # Parse the passed arguments into a urlobject
        Base._urlObject = urlObject = urlparse.urlsplit(url)
        Base.handle = int(argv[1]) if argv[1].isdigit() else -1

        # Fetch class that matches route and call
        route_path = urlObject.path.lower() if urlObject.path else "/"
        cls = cls_for_route(route_path, raise_on_error=True)
        logger.debug('Dispatching to route "%s": class "%s"', route_path, cls.__name__)

        # Parse arguments
        if urlObject.query:
            Base._args = _args = Base.parse_qs(unicode(urlObject.query))
            if u"refresh" in _args:
                global refresh
                refresh = True
                _args[u"updatelisting"] = u"true"
            logger.debug("Called with args: %r", _args)
        else:
            Base._args = {}

        # Execute Main Program
        cls()

    # Handle any exception with the buggalo module
    except Exception as exception:
        xbmcplugin.endOfDirectory(Base.handle, succeeded=False)
        if buggalo_email and debug is False:
            import buggalo
            buggalo.GMAIL_RECIPIENT = buggalo_email
            # buggalo.onExceptionRaised(logging.dict_logs() if logging.logs else None)
        elif debug is False:
            Base.notification(exception.__class__.__name__, str(exception), "error", error_time)
            import traceback
            traceback.print_exc()
        else:
            raise

    else:
        logger.debug("# Total time to execute: %s", time.time() - before)


class Base(collections.MutableMapping):
    __fanart = __icon = __path = __path_global = __profile = _type = _version = _devmode = __session = None
    _route = __utils = __profile_global = _args = _urlObject = handle = None

    def __init__(self):
        pass

    @classmethod
    def url_for_route(cls, route_pattern, query=None):
        """
        Return addon url for callback by kodi as string

        route_pattern      --- Route for class that will be called when addon is called from kodi
        [query]    --- Query dict that will be urlencode and appended to url

        >>> Base.url_for_route("/videos", {"url":"http://www.google.ie}")
        "plugin://<addon.id>/videos?url=http%3A%2F%2Fwww.google.ie"
        """

        # UrlEncode query dict if required
        if query:
            query = cls.urlencode(query)

        # Create addon url for kodi
        _urlObject = cls._urlObject
        return urlparse.urlunsplit((_urlObject.scheme, _urlObject.netloc, str(route_pattern), query, ""))

    @classmethod
    def url_for_current(cls, params=None, *querys_as_string):
        """
        Return addon url for callback to current path by kodi as string

        params : dict --- dictionary of parameters to update the current params with to add to url
        query_as_string : string args --- Keyword args of query entries that will be appended to url

        >>> Base.url_for_current(None, "refresh=true")
        "plugin://<addon.id>/videos?url=http%3A%2F%2Fwww.google.ie&refresh=true"

        >>> Base.url_for_current({"url":"http://youtube.com/", "id":"5359"}, "refresh=true", "updatelisting=true")
        "plugin://<addon.id>/videos?url=http%3A%2F%2Fyoutube.com/&id=5359&refresh=true&updatelisting=true"
        """
        _urlObject = cls._urlObject
        querys_as_string = list(querys_as_string)
        if params:
            cls._args.update(params)
            query = cls.urlencode(cls._args)
            querys_as_string.append(query)
        elif _urlObject.query:
            querys_as_string.append(_urlObject.query)

        return urlparse.urlunsplit(
            (_urlObject.scheme, _urlObject.netloc, _urlObject.path, "&".join(querys_as_string), ""))

    @staticmethod
    def parse_qs(query, separator=u",", keep_blank_values=True, strict_parsing=True):
        """
        Parse query string and return a dict unicode values split by a separator

        query               --- Url query to parse as unicode
        [separator]         --- Unicode charactor to be used to compine a list of values. (default u",")
        [keep_blank_values] --- Flag to indicating whether blank values in queries should be treated as blank strings.
                                (default True)
        [strict_parsing]    --- Flag to indicating what to do with parsing errors. If false, errors are silently ignored
                                If true, errors raise a ValueError exception. (default True)

        >>> Base.parse_qs(u"url=http%3A%2F%2Fwww.google.ie&refresh=true")
        {u"url":u"http://www.google.ie, u"refresh":u"true"}

        >>> Base.parse_qs(u"url=http%3A%2F%2Fwww.google.ie&code=5&code=10")
        {u"url":u"http://www.google.ie, u"code":u"5,10"}
        """
        query_dict = urlparse.parse_qs(query, keep_blank_values, strict_parsing)
        return {key: separator.join(values) for key, values in query_dict.iteritems()}

    @staticmethod
    def urlencode(query):
        """
        Parse dict and return urlEncoded string of key and values separated by '&'

        query : dict --- query dict to parse

        >>> Base.urlencode({"url":u"http://www.google.ie", u"refresh":"true"})
        "url=http%3A%2F%2Fwww.google.ie&refresh=true"
        """

        # Create local variable of globals for better performance
        _quote_plus = urllib.quote_plus
        _isinstance = isinstance
        _unicode = unicode
        _str = str

        # Parse dict and encode into url compatible string
        segments = []
        for key, value in query.iteritems():
            if _isinstance(value, _unicode):
                value = _quote_plus(value.encode("utf8"))
            else:
                value = _quote_plus(str(value))

            # Combine key and value
            segments.append(_str(key) + "=" + value)

        # Return urlencoded string
        return "&".join(segments)

    @staticmethod
    def notification(heading, message, icon="info", display_time=5000, sound=True):
        """
        Send a notification for kodi to display

        Args:
            heading (str|unicode): dialog heading.
            message (str|unicode): dialog message.
            icon (string, optional): icon to use. (default info) option : (error, info, warning)
            display_time (integer, optional): display_time in milliseconds to show dialog (default 5000)
            sound (bool, optional): play notification sound (default True)
        """

        # Convert heading and messegs to UTF8 strings if needed
        if isinstance(heading, unicode):
            heading = heading.encode("utf8")
        if isinstance(message, unicode):
            message = message.encode("utf8")

        # Send Error Message to Display
        dialog = xbmcgui.Dialog()
        dialog.notification(heading, message, icon, display_time, sound)

    @staticmethod
    def get_local_string(string_id):
        """
        Returns an addon's localized "unicode string"

        string_id : integer or string - string_id for string you want to localize

        >>> Base.get_local_string(21866)
        "Category" # Localized

        >>> Base.get_local_string("Category")
        "Category" # Localized
        """
        if string_id in _strings:
            string_id = _strings[string_id]
        if 30000 <= string_id <= 30999:
            return addonData.getLocalizedString(string_id)
        elif 32000 <= string_id <= 32999:
            return scriptData.getLocalizedString(string_id)
        else:
            return xbmc.getLocalizedString(string_id)

    @staticmethod
    def get_setting(setting_id, raw_setting=False):
        """
        Returns the value of a setting as a Unicode/Int/Boolean type

        setting_id : string - setting_id of the setting that the module needs to access
        [raw_setting] : boolean --- Return the raw setting as unicode without changing type
        """
        setting = addonData.getSetting(setting_id)
        if raw_setting:
            return unicode(setting, "utf8")
        elif setting.isdigit():
            return int(setting)
        elif setting == "true":
            return True
        elif setting == "false":
            return False
        else:
            return unicode(setting, "utf8")

    @staticmethod
    def set_setting(setting_id, value):
        """
        Sets Addon setting

        setting_id : string - setting_id of the setting that the module needs to access
        value : string or unicode - value of the setting
        """
        addonData.setSetting(setting_id, value)

    @property
    def id(self):
        """ Return ID of addon as unicode """
        return unicode(addonID)

    @property
    def name(self):
        """ Return name of addon as unicode """
        return unicode(addonData.getAddonInfo("name"))

    @property
    def fanart(self):
        """ Return path to addon fanart as unicode """
        if self.__fanart is not None:
            return self.__fanart
        else:
            _fanart = addonData.getAddonInfo("fanart")
            _fanart = translate_path(_fanart)
            if not os.path.exists(_fanart):
                _fanart = ""
            self.__fanart = _fanart
            return _fanart

    @property
    def icon(self):
        """ Return Path to addon icon as unicode """
        if self.__icon is not None:
            return self.__icon
        else:
            _icon = addonData.getAddonInfo("icon")
            _icon = translate_path(_icon)
            if not os.path.exists(_icon):
                _icon = ""
            self.__icon = _icon
            return _icon

    @property
    def path(self):
        """ Return path to addon source directory as unicode """
        if self.__path is not None:
            return self.__path
        else:
            _path = addonData.getAddonInfo("path")
            _path = translate_path(_path)
            self.__path = _path
            return _path

    @property
    def profile(self):
        """ Return path to addon profile data directory as unicode """
        if self.__profile is not None:
            return self.__profile
        else:
            _profile = addonData.getAddonInfo("profile")
            _profile = translate_path(_profile)
            self.__profile = _profile
            return _profile

    @property
    def _path_global(self):
        """ Return path to script source directory as unicode """
        if self.__path_global is not None:
            return self.__path_global
        else:
            _path = scriptData.getAddonInfo("path")
            _path = translate_path(_path)
            self.__path_global = _path
            return _path

    @property
    def _profile_global(self):
        """ Return path to script profile data directory as unicode """
        if self.__profile_global is not None:
            return self.__profile_global
        else:
            _profile = scriptData.getAddonInfo("profile")
            _profile = translate_path(_profile)
            self.__profile_global = _profile
            return _profile

    @property
    def utils(self):
        """ Return utils module object"""
        if self.__utils:
            return self.__utils
        else:
            from . import utils
            self.__utils = utils
            return utils

    def requests(self, max_age=60, max_retries=0):
        """
        Return requests session object with builtin caching support

        Kwargs:
            max_age (integer): The max age in minutes that the cache can be before it becomes stale (default 60)
            max_retries (integer): The maximum number of retries each connection should attempt (default 0)

        Note: Valid max_age values.
        -1, to allways return a cached response regardless of the age.
        0, to allow use of the cache but will always make a request to server to check the Not Modified Sence header,
        witch always return the latest content while using the cache, when content has not changed sense last cached.
        >0, will return cached response untill the cached response is older than giving age.
        None, to block use of the cache, will always return server response as is.

        Note:
        max_retries applies only to failed DNS lookups, socket connections and connection timeouts,
        never to requests where data has made it to the server. By default, Requests does not retry failed connections.
        """
        if self.__session is not None:
            return self.__session
        else:
            # Create a non caching requests session
            if max_age is None or self.get_setting("disable-cache") is True:
                import requests
                requests.packages.urllib3.disable_warnings()
                session = requests.session()

            # Create a caching request session
            else:
                from . import requests_caching
                session = requests_caching.cache_session(self.profile, 0 if u"refresh" in self else max_age,
                                                         max_retries)

            # Add user agent to session headers and return session
            session.headers[
                "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
            self.__session = session
            return session

    def request_basic(self, max_age=60, max_retries=0):
        from . import urllib_caching
        session = urllib_caching.cache_session(self.profile, 0 if u"refresh" in self else max_age, max_retries)

        # Add user agent to session headers and return session
        session.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
        return session

    def shelf_storage(self, filename=u"metadata_dict.shelf", custom_dir=None, protocol=2, writeback=False):
        """
        Return persistence dictionary storage object that is stored on disk.

        Args:
            filename (unicode): Filename for shelf_storage object to use. (default metadata_dict.shelf)
            custom_dir (unicode): Directory to store the storage file, defaults to addon profile directory
            protocol (integer): Protocol version to use when pickling the data to disk. (default 2)
            writeback (boolean): Sync data back to disk on close. (default False)
        """
        from .storage import shelfStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return shelfStorage(data_path, protocol=protocol, writeback=writeback)

    def dict_storage(self, filename=u"metadata_dict.json", custom_dir=None):
        """
        Return persistence dictionary storage object that is stored on disk.

        Kwargs:
            filename (unicode): Filename for dict_storage object to use. (default metadata_dict.json)
            custom_dir (unicode): Directory to store the storage file, defaults to addon profile directory
        """
        from .storage import dictStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return dictStorage(data_path)

    def list_storage(self, filename=u"metadata_list.json", custom_dir=None):
        """
        Return persistence list storage object that is stored on disk.

        Kwargs:
            filename (unicode): Filename for list_storage object to use. (default metadata_list.json)
            custom_dir (unicode): Directory to store the storage file, defaults to addon profile directory
        """
        from .storage import listStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return listStorage(data_path)

    def set_storage(self, filename=u"metadata_set.json", custom_dir=None):
        """
        Return persistence set storage object that is stored on disk.

        Kwargs:
            filename (unicode): Filename for set_storage object to use. (default metadata_set.json)
            custom_dir (unicode): Directory to store the storage file, defaults to addon profile directory
        """
        from .storage import setStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return setStorage(data_path)

    @classmethod
    def copy(cls):
        return cls._args.copy()

    def __getitem__(self, key):
        return self._args[key]

    def __setitem__(self, key, value):
        self._args[key] = value

    def __delitem__(self, key):
        del self._args[key]

    def __iter__(self):
        return iter(self._args)

    def __len__(self):
        return len(self._args)


class KodiLogHandler(logging.Handler):
    """ Custom Logger Handler to forward logs to kodi """
    log_level_map = {0: 0,
                     10: xbmc.LOGDEBUG,
                     20: xbmc.LOGINFO,
                     30: xbmc.LOGWARNING,
                     40: xbmc.LOGERROR,
                     50: xbmc.LOGSEVERE}

    def emit(self, record):
        """ Forward the log record to kodi to let kodi handle the logging """
        xbmc.log(record.getMessage(), self.log_level_map[record.levelno])

# Dict to store all routes to classes
_strings = {}
_routes = {}

# Initiate xbmcaddon class to allow access to addon infomation
scriptData = xbmcaddon.Addon("script.module.codequick")
addonData = xbmcaddon.Addon()
addonID = addonData.getAddonInfo("id")
refresh = False

# Logging
formatter = logging.Formatter("[%(name)s.%(lineno)d]: %(message)s")
logger = logging.getLogger(addonID)
kodi_handler = KodiLogHandler()
kodi_handler.setLevel(logging.DEBUG)
kodi_handler.setFormatter(formatter)
logger.addHandler(kodi_handler)

# Objects/Variables that are accessible when using from foo import *
__all__ = ["Base", "localized", "route", "run"]
