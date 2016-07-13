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

# Dict to store all routes to classes
_strings = {}
_routes = {}

# Initiate xbmcaddon class to allow access to addon infomation
scriptData = xbmcaddon.Addon("script.module.codequick")
addonData = xbmcaddon.Addon()
addonID = addonData.getAddonInfo("id")
refresh = False


def translate_path(path):
    """
    Translate a kodi special path into an absolute path.

    Notes
    -----
    Only useful if you are coding for both Linux and Windows.

    Parameters
    ----------
    path : bytestring
        Returns the translated path.

    Returns
    -------
    unicode
        The translated path.

    Example
    -------
    >>> translate_path('special://profile/')
    '/home/user/.kodi/user/.kodi/userdata/addon_data/'
    """
    if path[:10] == "special://":
        return unicode(xbmc.translatePath(path), "utf8")
    else:
        return unicode(path, "utf8")


def cls_for_route(route_pattern, raise_on_error=False):
    """
    Return class thats associated with specified route.

    Parameters
    ----------
    route_pattern : bytestring
        Route thats associated with a class.
    raise_on_error : bool, optional(default=False)
        True if a KeyError will be raised if no class was found for specified route.

    Returns
    -------
    :class:`Base`, optional
        Return the class that matchs the given route pattern.
        Will return 'None' if no class was found for route pattern and raise_on_error was set to False.

    Raises
    ------
    KeyError
        When no class if found that matchs route pattern.
    """
    route_pattern = str(route_pattern)
    for cls, pattern in _routes.iteritems():
        if pattern == route_pattern.lower():
            return cls
    else:
        # No available class matching specified route pattern was found
        if raise_on_error:
            raise KeyError("No class for route: %s" % route_pattern)
        else:
            return None


def localized(strings):
    """
    Add dict of localized string:id pairs to get_local_string.

    String:id pairs are used to allow accessing localized strings using string value instead of string id.

    Parameters
    ----------
    strings : dict
        string:id pairs to add to the local string database.

    Example
    -------
    Here we want to print a french localized string for the string 'testing'. This
    can be requested using the string id '31010' or by using the string reference 'testing'.
    But to use the reference you first have to asign the reference to a string id.

    >>> Base.get_local_string(31010)
    "essai"

    >>> localized({"testing":31010})
    >>> Base.get_local_string("testing")
    "essai"
    """
    _strings.update(strings)


def route(route_pattern):
    """
    Decorator to bind a class to a route that can be called via route dispatcher.

    Parameters
    ----------
    route_pattern : bytestring
        The route pattern that will point to the bind class.

    Returns
    -------
    class
        Decorated class.
    """
    route_pattern = str(route_pattern.lower())

    def decorator(cls):
        _routes[cls] = route_pattern
        cls.route = route_pattern
        return cls

    return decorator


def run():
    """ Call Class instance thats associated with route passed in from kodi sys args. """

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
        Base.urlObject = urlObject = urlparse.urlsplit(url)
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
        # noinspection PyCallingNonCallable
        cls()

    # Handle any exception with the buggalo module
    except Exception as e:
        xbmcplugin.endOfDirectory(Base.handle, succeeded=False)
        Base.notification(e.__class__.__name__, str(e), "error")
        logger.exception("Logging an uncaught exception")
        KodiLogHandler.show_debug()
    else:
        logger.debug("# Total time to execute: %s", time.time() - before)


class Base(collections.MutableMapping):
    """
    Base class for all working classes to inherit.

    Attributes
    ----------
    id : unicode
        ID of addon.
    name : unicode
        Name of addon.
    fanart : unicode
        Path to addon fanart.
    icon : unicode
        Path to addon icon.
    path : unicode
        Path to addon source directory.
    profile : unicode
        Path to addon profile data directory.
    profile_global : unicode
        Path to script profile data directory.
    """
    __fanart = __icon = __path = __path_global = __profile = _type = _version = _devmode = __session = None
    _route = __utils = __profile_global = _args = urlObject = handle = None

    def __init__(self):
        pass

    @classmethod
    def url_for_route(cls, route_pattern, query=None):
        """
        Return addon url for callback by kodi as string

        Parameters
        ----------
        route_pattern : unicode
            Route of class that will be called when addon is called from kodi
        query : dict, optional
            Query dict that will be urlencode and appended to url

        Returns
        -------
        str
            Plugin url that is used for kodi

        Example
        -------
        >>> Base.url_for_route(u"/videos", {"url":"http://www.google.ie}")
        "plugin://<addon.id>/videos?url=http%3A%2F%2Fwww.google.ie"
        """

        # UrlEncode query dict if required
        if query:
            query = cls.urlencode(query)

        # Create addon url for kodi
        _urlObject = cls.urlObject
        return urlparse.urlunsplit((_urlObject.scheme, _urlObject.netloc, str(route_pattern), query, ""))

    @classmethod
    def url_for_current(cls, params=None, *querys_as_string):
        """
        Return addon url for callback to current path by kodi as string.

        Parameters
        ----------
        params : dict, optional
            Dictionary of params to update the current params with.
        querys_as_string : args, optional
            Keyword args of query entries that will be appended to url.

        Returns
        -------
        str
            Plugin url that is used for kodi

        Examples
        --------
        >>> Base.url_for_current(None, "refresh=true")
        "plugin://<addon.id>/videos?url=http%3A%2F%2Fwww.google.ie&refresh=true"

        >>> Base.url_for_current({"url":"http://youtube.com/", "id":"5359"}, "refresh=true", "updatelisting=true")
        "plugin://<addon.id>/videos?url=http%3A%2F%2Fyoutube.com/&id=5359&refresh=true&updatelisting=true"
        """
        _urlObject = cls.urlObject
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
        Parse query string and return a dict unicode values split by a separator.

        Parameters
        ----------
        query : bytestring
            Url query to parse as unicode.
        separator : unicode, optional(default=u'')
            Unicode charactor to be used to compine a list of values.
        keep_blank_values : bool, optional(default=True)
            Flag to indicating whether blank values in queries should be treated as blank strings.
        strict_parsing : bool, optional(default=True)
            Flag to indicate what to do with parsing errors. If false, errors are silently ignored,
            if true ValueError is raised.

        Returns
        -------
        dict
            key:value pairs populated from query.

        Raises
        ------
        ValueError
            If strict_parsing is True, then ValueError will be raised if there is any error in the parsing.

        Examples
        --------
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
        Parse dict and return urlEncoded string of key and values separated by '&'.

        Parameters
        ----------
        query : dict
            query dict to parse.

        Returns
        -------
        str
            Url encoded string of key and values separated by '&'.

        Example
        -------
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

        Parameters
        ----------
        heading : bytestring
            Dialog heading.
        message : bytestring
            Dialog message.
        icon : bytestring, optional(default="info")
            Icon to use. option are 'error', 'info', 'warning'.
        display_time : bytestring, optional(default=5000)
            Display_time in milliseconds to show dialog.
        sound : bytestring, optional(default=True)
            Whether or not to play notification sound.
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
        Returns an addon's localized

        Parameters
        ----------
        string_id : int, str
            The id or reference of the string to localize.

        Returns
        -------
        unicode
            localized string

        Examples
        --------
        >>> Base.get_local_string(31010)
        "essai" # testing localized to french

        >>> localized({"testing":31010})
        >>> Base.get_local_string("testing")
        "essai" # testing localized to french
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
        Returns the value of a setting as a unicode/int/boolean type.

        Parameters
        ----------
        setting_id : str
            Id of the requested setting.
        raw_setting : bool, optional(default=False)
            Return the raw setting as unicode without converting the data type.

        Returns
        -------
        unicode, int, bool
            The requested addon setting.

            If raw_setting is True then return value will always be of type unicode. Else the value will be
            converted to is relevent type. e.g.

            return as unicode if raw_setting is True or if value is just a simple string.
            return as interger if value is a digit.
            return as a boolean if value is a 'true' or 'false' string.
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

        Parameters
        ----------
        setting_id : str
            Id of the setting to be changed.
        value : bytestring
            New value of the setting.
        """
        addonData.setSetting(setting_id, value)

    @property
    def id(self):
        """
        Return ID of addon as unicode.

        Returns
        -------
        unicode
            Current addon id.
        """
        return unicode(addonID)

    @property
    def name(self):
        """
        Return name of addon as unicode.

        Returns
        -------
        unicode
            Name of current addon.
        """
        return unicode(addonData.getAddonInfo("name"))

    @property
    def fanart(self):
        """
        Return path to addon fanart as unicode.

        Returns
        -------
        unicode
            Path to addon fanart image.
        """
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
        """
        Return Path to addon icon as unicode

        Returns
        -------
        unicode
            Path to addon icon image.
        """
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
        """
        Return path to addon source directory as unicode.

        Returns
        -------
        unicode
            Path to addon source directory.
        """
        if self.__path is not None:
            return self.__path
        else:
            _path = addonData.getAddonInfo("path")
            _path = translate_path(_path)
            self.__path = _path
            return _path

    @property
    def profile(self):
        """
        Return path to addon profile data directory as unicode.

        Returns
        -------
        unicode
            Path to addon data directory.
        """
        if self.__profile is not None:
            return self.__profile
        else:
            _profile = addonData.getAddonInfo("profile")
            _profile = translate_path(_profile)
            self.__profile = _profile
            return _profile

    @property
    def _path_global(self):
        """
        Return path to script source directory as unicode.

        Returns
        -------
        unicode
            Path to script source directory.
        """
        if self.__path_global is not None:
            return self.__path_global
        else:
            _path = scriptData.getAddonInfo("path")
            _path = translate_path(_path)
            self.__path_global = _path
            return _path

    @property
    def profile_global(self):
        """
        Return path to script profile data directory as unicode.

        Returns
        -------
        unicode
            Path to script data directory.
        """
        if self.__profile_global is not None:
            return self.__profile_global
        else:
            _profile = scriptData.getAddonInfo("profile")
            _profile = translate_path(_profile)
            self.__profile_global = _profile
            return _profile

    @property
    def utils(self):
        """
        Return utils module object.

        Returns
        -------
        :class:`utils`
            modual object.
        """
        if self.__utils:
            return self.__utils
        else:
            from . import utils
            self.__utils = utils
            return utils

    def requests(self, max_age=60, max_retries=0):
        """
        Return requests session object with builtin caching support.

        Parameters
        ----------
        max_age : int, optional(default=60)
            The max age in minutes that the cache can be before it becomes stale. Valid max_age values are.

            -1, to allways return a cached response regardless of the age.

            0, allow use of the cache but will always make a request to server to check the Not Modified Sence header,
            witch always return the latest content when using the cache, when content has not changed sense last cached.

            0, will return cached response untill the cached response is older than giving age.
            None, to block use of the cache, will always return server response as is.

        max_retries : int, optional(default=0)
            The maximum number of retries each connection should attempt

            max_retries applies only to failed DNS lookups, socket connections and connection timeouts, never to
            requests where data has made it to the server. By default, requests does not retry failed connections.

        Returns
        -------
        :class:`requests.session`
            Request session object.

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
                age = 0 if u"refresh" in self else max_age
                session = requests_caching.cache_session(self.profile, age, max_retries)

            # Add user agent to session headers and return session
            session.headers[
                "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
            self.__session = session
            return session

    def request_basic(self, max_age=60):
        """
        Return a basic emulated requests session object.

        This request object is custom made to be faster than the real request session object by using basic urllib2
        but does not actually have any session support to keep connections alive, just caching support.
        Just faster to load in comparison to the requests module sence it is greatly simplified.

        Parameters
        ----------
        max_age : int, optional(default=60)
            The max age in minutes that the cache can be before it becomes stale.

        Returns
        -------
        :class:`urllib_caching.cache_session`
            Emulated request session object.
        """
        from . import urllib_caching
        session = urllib_caching.cache_session(self.profile, 0 if u"refresh" in self else max_age)

        # Add user agent to session headers and return session
        session.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0"
        return session

    def shelf_storage(self, filename=u"metadata_dict.shelf", custom_dir=None, protocol=2, writeback=False):
        """
        Return persistence dictionary storage object that is stored on disk.

        Parameters
        ----------
        filename : basestring, optional(default='metadata_dict.shelf')
            Filename for shelf_storage object to use. default 
        custom_dir : basestring, optional
            Directory to store the storage file, defaults to addon profile directory.
        protocol : int, optional(default=2)
            Protocol version to use when pickling the data to disk. default 2
        writeback : bool, optional(default=False)
            Sync data back to disk on close. default False

        Returns
        -------
        :class:`ShelfStorage`
            A persistence shelf storage object
        """
        from .storage import ShelfStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return ShelfStorage(data_path, protocol=protocol, writeback=writeback)

    def dict_storage(self, filename=u"metadata_dict.json", custom_dir=None):
        """
        Return persistence dictionary storage object that is stored on disk.

        Parameters
        ----------
        filename : unicode, optional(default='metadata_dict.json')
            Filename for dict_storage object to use.
        custom_dir : unicode, optional
            Directory to store the storage file, defaults to addon profile directory.

        Returns
        -------
        :class:`DictStorage`
            A persistence dict storage object.
        """
        from .storage import DictStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return DictStorage(data_path)

    def list_storage(self, filename=u"metadata_list.json", custom_dir=None):
        """
        Return persistence list storage object that is stored on disk.

        Parameters
        ----------
        filename : unicode, optional(default=u'metadata_list.json')
            Filename for list_storage object to use.
        custom_dir : unicode
            Directory to store the storage file, defaults to addon profile directory.

        Returns
        -------
        :class:`ListStorage`
            A persistence list strage object.
        """
        from .storage import ListStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return ListStorage(data_path)

    def set_storage(self, filename=u"metadata_set.json", custom_dir=None):
        """
        Return persistence set storage object that is stored on disk.

        Parameters
        ----------
        filename : unicode, optional(default=u'metadata_set.json')
            Filename for set_storage object to use.
        custom_dir : unicode, optional
            Directory to store the storage file, defaults to addon profile directory

        Returns
        -------
        :class:`SetStorage`
            A persistence set storage object
        """
        from .storage import SetStorage
        data_path = os.path.join(custom_dir if custom_dir else self.profile, filename)
        return SetStorage(data_path)

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
    _debug_msgs = []
    log_level_map = {0: 0,
                     10: xbmc.LOGDEBUG,
                     20: xbmc.LOGNOTICE,
                     30: xbmc.LOGWARNING,
                     40: xbmc.LOGERROR,
                     50: xbmc.LOGSEVERE}

    def emit(self, record):
        """ Forward the log record to kodi to let kodi handle the logging """
        formated_msg = self.format(record)
        xbmc.log(formated_msg, self.log_level_map[record.levelno])
        if record.levelno == 10:
            self._debug_msgs.append(record.getMessage())

    @classmethod
    def show_debug(cls):
        """
        Log all debug messages as error messages.

        Useful to show debug messages in normal mode if any severe error occurred.
        """
        if cls._debug_msgs:
            xbmc.log("###### debug ######", xbmc.LOGNOTICE)
            for msg in cls._debug_msgs:
                xbmc.log(msg, xbmc.LOGNOTICE)
            xbmc.log("###### debug ######", xbmc.LOGNOTICE)

# Logging
formatter = logging.Formatter("[%(name)s] %(message)s")
logger = logging.getLogger(addonID)
logger.setLevel(logging.DEBUG)
kodi_handler = KodiLogHandler()
kodi_handler.setFormatter(formatter)
logger.addHandler(kodi_handler)
