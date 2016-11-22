# Standard Library Imports
import logging
import urlparse
import functools
import urllib
import time
import sys

# Kodi imports
import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmc

# Dict store for func and route mappings to route class object
_route_store = {}

__all__ = ["strings", "logger", "params", "run", "localize", "get_info",
           "get_setting", "set_setting", "requests_session"]


class KodiLogHandler(logging.Handler):
    """ Custom Logger Handler to forward logs to kodi """
    _debug_msgs = []
    log_level_map = {0: 0,
                     10: xbmc.LOGDEBUG,    # logger.debug
                     20: xbmc.LOGNOTICE,   # logger.info
                     30: xbmc.LOGWARNING,  # logger.warning
                     40: xbmc.LOGERROR,    # logger.error
                     50: xbmc.LOGSEVERE}   # logger.critical

    def emit(self, record):
        """ Forward the log record to kodi to let kodi handle the logging """
        formated_msg = self.format(record)
        if isinstance(formated_msg, unicode):
            formated_msg = formated_msg.encode("utf8")

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
                xbmc.log(msg, xbmc.LOGWARNING)
            xbmc.log("###### debug ######", xbmc.LOGNOTICE)


def setup_logging(addon_id):
    """
    Setup the logging module to log to kodi log.

    Parameters
    ----------
    addon_id : str
        The id of the running addon.

    Returns
    -------
    :class:`logging.Logger`
        The logger object that is used for logging to kodi.
    """

    # Create output formatter
    formatter = logging.Formatter("[%(name)s] %(message)s")
    # Fetch the logger with addon id as logger id
    _logger = logging.getLogger(addon_id)
    # Set the logging level to debug so kodi can handle what is logged instead
    _logger.setLevel(logging.DEBUG)
    # Instantiate kodi log handler
    kodi_handler = KodiLogHandler()
    kodi_handler.setFormatter(formatter)
    # Add the kodi log handler to logger
    _logger.addHandler(kodi_handler)
    # Return the logger
    return _logger


def process_sys_args(argv):
    """
    Convert the system params that are passed in from kodi into a urlparse object.

    Parameters
    ----------
    argv : sized
        The system params passed in from kodi

    Returns
    -------
    tuple
        The urlparse named tuple

    Raises
    ------
    ValueError
        When No action value was given from script call
    """

    # Check if running as a plugin
    if argv[0].startswith("plugin://"):
        url = argv[0] + argv[2]

    # Must be running as a script
    else:
        arg_len = len(argv)
        if arg_len == 1:
            raise ValueError("No action value was giving from script call")
        elif arg_len == 2:
            url = "plugin://%s%s" % (addonID, argv[1])
        else:
            query = "&".join(["arg%i=%s" % (count, arg) for count, arg in enumerate(argv[2:], start=1)])
            url = "plugin://%s%s?%s" % (addonID, sys.argv[1], query)

    # Return the url as a split named tuple
    return urlparse.urlsplit(unicode(url, "latin1"))


def urlunsplit(*argss):
    """ Unsplit a tuple of url parts """
    return urlparse.urlunsplit(argss)


# Fetch addon data objects
scriptData = xbmcaddon.Addon("script.module.codequick")
addonData = xbmcaddon.Addon()
addonID = addonData.getAddonInfo("id")

# Process kodi info
strings = {}
cleanup_functions = []
logger = setup_logging(addonID)
parsedUrl = process_sys_args(sys.argv)
handle = int(sys.argv[1]) if sys.argv[1].isdigit() else -1
selected_route = parsedUrl.path if parsedUrl.path else u"/"
params = dict(urlparse.parse_qsl(parsedUrl.query)) if parsedUrl.query else {}
if params:
    logger.debug("Program arguments: %s", repr(params))

# Create a partial function that unsplits a url but has the first 2 parts already passed in as strings
path_unsplit = functools.partial(urlunsplit, str(parsedUrl.scheme), str(parsedUrl.netloc))
current_unsplit = functools.partial(urlunsplit, str(parsedUrl.scheme), str(parsedUrl.netloc), str(parsedUrl.path))


class RouteData(object):
    """
    Class thats used for accessing the route function

    Parameters
    ----------
    func : function
        The function that will be added to the route dispatcher.

    route : bytestring
        The path that the route dispatcher will used to map to function

    Attributes
    ----------
    func : function
        The function that will be called.

    route : unicode
        The route string that points to this class.

    name : unicode
        The name of the function that will be called.
    """
    def __init__(self, func, route):
        self.name = unicode(func.__name__)
        self.route = route
        self._func = func

    def __call__(self, *args, **kwargs):
        """Allow this class to be called as if it was a function"""
        return self._func(*args, **kwargs)

    def kodi_path(self, query=None):
        """
        Return addon url for callback by kodi

        Parameters
        ----------
        query : dict, optional
            Query dict that will be urlencode and appended to url

        Returns
        -------
        str
            Plugin url that is used for kodi
        """

        # UrlEncode query dict if required
        if query:
            query = urllib.urlencode(query)

        # Create addon url for kodi
        return path_unsplit(self.route, query, None)

    @classmethod
    def register(cls, route):
        def decorator(func):
            # Registor this class route
            if route in _route_store:
                debug_args = (route, func.__name__, _route_store[route].name)
                raise RuntimeError("Route %s for function %s is already registered to function %s" % debug_args)
            else:
                route_cls = cls(func, route)
                _route_store[route] = route_cls
                return route_cls

        return decorator


def current_path(**querys):
    """
    Return addon url for callback to current path by kodi as string.

    Parameters
    ----------
    querys : params, optional
        Keyword params of query entries that will be appended to url.

    Returns
    -------
    str
        Plugin url that is used for kodi
    """

    # Check if querys are needed to be mirged with the base query
    if querys:
        if params:
            args_copy = params.copy()
            args_copy.update(querys)
            query_string = urllib.urlencode(args_copy)
        else:
            query_string = urllib.urlencode(querys)
    else:
        query_string = parsedUrl.query

    # Rejoin the split url back into a full url
    return current_unsplit(query_string, "")


def run(debug=False):
    """ Fetch and execute the requested route function """

    # Fetch current time so to monitor the time it takes to execute
    before = time.time()

    # Fetch the requested function that will be executed
    route_cls = _route_store[selected_route]
    logger.debug('Dispatching to route "%s": function "%s"', selected_route, route_cls.name)

    try:
        # Execute the registered function
        route_cls.execute()

    except Exception as e:
        KodiLogHandler.show_debug()
        logger.exception("Logging unexpected exception")
        dialog = xbmcgui.Dialog()
        dialog.notification(e.__class__.__name__, str(e), "error")
        xbmcplugin.endOfDirectory(handle, succeeded=False)
    else:
        # Log the execution time of this addon
        logger.debug("# Total time to execute: %s", time.time() - before)

        # Execute all registored cleanup functions if any
        if cleanup_functions:
            for func in cleanup_functions:
                try:
                    func()
                except Exception as e:
                    logger.exception("Cleanup function failed:" % str(e))

        # If debug param is true then log all the debug messages as notice messages so
        # kodi will output the debug messages to the normal none debug log.
        if debug:
            KodiLogHandler.show_debug()


def localize(string_id):
    """
    Returns an addon's localized.

    Parameters
    ----------
    string_id : int, str
        The id or reference of the string to localized.

    Returns
    -------
    unicode
        Localized string.

    Examples
    --------
    >>> localize(136)
    "Wiedergabelisten" # playlists localized to german

    >>> strings.update(playlists=136)
    >>> localize("playlists")
    "Wiedergabelisten" # playlists localized to german
    """
    if string_id in strings:
        string_id = strings[string_id]

    if 30000 <= string_id <= 30999:
        return addonData.getLocalizedString(string_id)
    elif 32000 <= string_id <= 32999:
        return scriptData.getLocalizedString(string_id)
    else:
        return xbmc.getLocalizedString(string_id)


def get_info(info_id):
    if info_id == "path_global":
        resp = scriptData.getAddonInfo("path")
    elif info_id == "profile_global":
        resp = scriptData.getAddonInfo("profile")
    else:
        resp = addonData.getAddonInfo(info_id)

    # Check if path needs to be translated first
    if resp[:10] == "special://":
        resp = xbmc.translatePath(resp)

    # Return the response as unicode
    return unicode(resp, "utf8")


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

        return as unicode if raw_setting is True or if value is just a simple string.
        return as interger if value is a digit.
        return as boolean if value is a 'true' or 'false' string.
    """
    setting = addonData.getSetting(setting_id)

    if raw_setting:
        return setting
    elif setting.isdigit():
        return int(setting)
    elif setting == u"true":
        return True
    elif setting == u"false":
        return False
    else:
        return setting


def set_setting(setting_id, value):
    """
    Sets Addon setting

    Parameters
    ----------
    setting_id : str
        Id of the setting to be changed.
    value : unicode
        New value of the setting.
    """
    addonData.setSetting(setting_id, value)


def get_addon_setting(addon_id, key):
    """
    Return setting for selected addon.

    Parameters
    ----------
    addon_id: str
        Id of the addon that contains the required setting.

    key : str
        Id of the required setting.

    Returns
    -------
    unicode
        setting from specified addon.

    Raises
    ------
    RuntimeError
        If given addon id was not found.
    UnicodeError
        If unable to convert property from utf8 to unicode.
    """
    return xbmcaddon.Addon(addon_id).getSetting(key)


def get_addon_data(addon_id, key):
    """
    Returns the value of an addon property as unicode.

    Parameters
    ----------
    addon_id : str
        Id of the addon that contains the required value.

    key : str
        Id of the required property.

    Returns
    -------
    unicode
        The required property of requested addon.

    Raises
    ------
    RuntimeError
        If given addon id was not found.
    UnicodeError
        If unable to convert property from utf8 to unicode.
    """
    return unicode(xbmcaddon.Addon(addon_id).getAddonInfo(key), "utf8")


def requests_session(max_age=None, disable_cache=False):
    """
    Return requests session object with builtin caching support

    Parameters
    ----------
    max_age : int, optional(default=3600)
        The max age in seconds that the cache can be before it becomes stale. Valid values are.

        -1, to allways return a cached response regardless of the age of the cache.

        0, allow use of the cache but will always make a request to server to check the Not Modified Sence header,
        witch will check if the cache matchs the server before downloading the content again.

        >=1, will return cached response untill the cached response is older than giving max age.

    disable_cache : bool, optional(default=False)
        If true the cache system will be bypassed (disabled).
    """
    from .requests_caching import session
    return session(max_age, disable_cache)
