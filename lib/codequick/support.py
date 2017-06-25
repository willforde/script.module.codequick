# -*- coding: utf-8 -*-

# Standard Library Imports
from collections import namedtuple
from binascii import hexlify
import urlparse
import logging
import inspect
import time
import json

# Kodi imports
import xbmcaddon
import xbmcgui
import xbmc

# Package imports
from .utils import KodiLogHandler, parse_sysargs

# Fetch addon data objects
script_data = xbmcaddon.Addon("script.module.codequick")
addon_data = xbmcaddon.Addon()

# The id of the running addon
plugin_id = addon_data.getAddonInfo("id")
logger_id = plugin_id.replace(".", "-")

# Base Logger
base_logger = logging.getLogger(logger_id)
base_logger.addHandler(KodiLogHandler())
base_logger.propagate = False
base_logger.setLevel(logging.DEBUG)

# Logger specific to this module
logger = logging.getLogger("%s.support" % logger_id)

# Named tuple for registered routes
Route = namedtuple("Route", ["controller", "callback", "source"])

# Extract calling arguments from sys args
selector, handle, params = parse_sysargs()


def build_path(path=None, query=None, **extra_query):
    """
    Build addon url that can be parsed to kodi for kodi to call the next set of listings.
    
    :param path: (Optional) The route selector path referencing the callback object. (default: current route selector)
    :param query: (Optional) A set of query key/value pairs to add to plugin path.
    :param extra_query: (Optional) Keyword arguments if given will be added to the current set of querys.

    :return: Plugin url used by kodi.
    :rtype: str
    """

    # If extra querys are given then append to current set of querys
    if extra_query:
        query = params.copy()
        query.update(extra_query)

    # Urlencode the query parameters
    # Note: Look into a custom urlencode, with better unicode support
    if query:
        query = "_json=" + hexlify(json.dumps(query))

    # Build url with new query parameters
    return urlparse.urlunsplit(("plugin", plugin_id, path if path else selector, query, ""))


class Dispatcher(object):
    def __init__(self):
        self.registered_routes = {}
        self.callback = None

    def __getitem__(self, route):
        return self.registered_routes[route]

    def __missing__(self, route):
        raise KeyError("missing required route: '{}'".format(route))

    def register(self, callback, cls=None, custom_route=None):
        """
        Register route callback function

        :param callback: The callback function.
        :param cls: (Optional) Parent class that will handle the callback, if registering a function.
        :param str custom_route: A custom route used for mapping.
        :returns: The callback function with extra attributes added, 'is_playable', 'is_folder' and 'route'.
        """
        if custom_route:
            route = custom_route.lower()
        elif callback.__name__.lower() == "root":
            route = callback.__name__.lower()
        else:
            route = "{}.{}".format(callback.__module__.strip("_"), callback.__name__).lower()

        if route in self.registered_routes:
            raise ValueError("encountered duplicate route: '{}'".format(route))

        callback.route = route
        if inspect.isclass(callback):
            # Check for required run method
            if hasattr(callback, "run"):
                # Set the callback as the parent and the run method as the function to call
                self.registered_routes[route] = Route(callback, callback.run, callback)
            else:
                raise NameError("missing required 'run' method for class: '{}'".format(callback.__name__))
        else:
            # Add listing type's to callback
            callback.is_playable = cls.is_playable
            callback.is_folder = cls.is_folder

            # Register the callback
            self.registered_routes[route] = Route(cls, callback, callback)

        # Return original function undecorated
        return callback

    def dispatch(self):
        """Dispatch to selected route path."""
        try:
            # Fetch the controling class and callback function/method
            route = self[selector]
            logger.debug("Dispatching to route: '%s'", selector)
            execute_time = time.time()
            self.callback = route.source

            # Initialize controller and execute callback
            controller_ins = route.controller()
            controller_ins.execute_route(route.callback)
        except Exception as e:
            # Log the error in both the gui and the kodi log file
            dialog = xbmcgui.Dialog()
            dialog.notification(e.__class__.__name__, str(e), "error")
            logger.critical(str(e), exc_info=1)
        else:
            from . import start_time
            logger.debug("Route Execution Time: %ims", (time.time() - execute_time) * 1000)
            logger.debug("Total Execution Time: %ims", (time.time() - start_time) * 1000)
            controller_ins.run_callbacks()


class Settings(object):
    def __getitem__(self, key):
        """
        Returns the value of a setting as a unicode string.

        :param str key: Id of the setting to access.

        :return: Setting as a unicode string.
        :rtype: unicode
        """
        return addon_data.getSetting(key)

    def __setitem__(self, key, value):
        """
        Set an add-on setting.

        :param str key: Id of the setting.
        :param value: Value of the setting.
        :type value: str or unicode
        """
        # noinspection PyTypeChecker
        addon_data.setSetting(key, value if isinstance(value, basestring) else str(value).lower())

    def get_boolean(self, key, addon_id=None):
        """
        Returns the value of a setting as a boolean.

        :param str key: Id of the setting to access.
        :param str addon_id: (Optional) Id of another addon to extract settings from.

        :raises RuntimeError: If addon_id is given and there is no addon with given id.

        :return: Setting as a boolean.
        :rtype: bool
        """
        setting = self.get(key, addon_id).lower()
        return setting == u"true" or setting == u"1"

    def get_int(self, key, addon_id=None):
        """
        Returns the value of a setting as a integer.

        :param str key: Id of the setting to access.
        :param str addon_id: (Optional) Id of another addon to extract settings from.

        :raises RuntimeError: If addon_id is given and there is no addon with given id.

        :return: Setting as a integer.
        :rtype: int
        """
        return int(self.get(key, addon_id))

    def get_number(self, key, addon_id=None):
        """
        Returns the value of a setting as a float.

        :param str key: Id of the setting to access.
        :param str addon_id: (Optional) Id of another addon to extract settings from.

        :raises RuntimeError: If addon_id is given and there is no addon with given id.

        :return: Setting as a float.
        :rtype: float
        """
        return float(self.get(key, addon_id))

    @staticmethod
    def get(key, addon_id=None):
        """
        Returns the value of a setting as a unicode string.

        :param str key: Id of the setting to access.
        :param str addon_id: (Optional) Id of another addon to extract settings from.

        :raises RuntimeError: If addon_id is given and there is no addon with given id.

        :return: Setting as a unicode string.
        :rtype: unicode
        """
        if addon_id:
            return xbmcaddon.Addon(addon_id).getSetting(key)
        else:
            return addon_data.getSetting(key)


class Script(object):
    # Set listing type variables
    is_playable = False
    is_folder = False

    #: Dictionary of params passed to callback
    params = params

    #: Dictionary like object of add-on settings.
    setting = Settings()

    #: Underlining logger object, for advanced use.
    logger = base_logger

    def __init__(self):
        self._title = self.params.get(u"_title_", u"")
        self._callbacks = []

    def execute_route(self, callback):
        """Execute the callback function and process the results."""
        logger.debug("Callback parameters: '%s'", params.callback_params)
        return callback(self, **params.callback_params)

    def register_callback(self, func, **kwargs):
        """
        Register a callback function that will be executed after kodi's endOfDirectory is called.
        Very useful for fetching extra metadata without slowing down the lising of listitems.

        :param func: Function that will be called of endOfDirectory.
        :param kwargs: Keyword arguments that will be passed to callback function.
        """
        callback = (func, kwargs)
        self._callbacks.append(callback)

    def run_callbacks(self):
        """Execute all callbacks, if any."""
        if self._callbacks:
            # Time before executing callbacks
            start_time = time.time()

            # Execute each callback one by one
            for func, kwargs in self._callbacks:
                try:
                    func(**kwargs)
                except Exception as e:
                    logger.exception(str(e))

            # Log execution time of callbacks
            logger.debug("Callbacks Execution Time: %ims", (time.time() - start_time) * 1000)

    @staticmethod
    def log(msg, *args, **kwargs):
        """
        Logs a message with logging level 'lvl'.

        Logging Levels:
        DEBUG 	    10
        INFO 	    20
        WARNING 	30
        ERROR 	    40
        CRITICAL 	50

        Note:
        When a log level of 50(CRITICAL) is given, then all debug messages that were previously logged
        will now be logged as level 30(WARNING). This will allow for debug messages to show in the normal kodi
        log file when a CRITICAL error has occurred, without having to enable kodi's debug mode.

        :param msg: The message format string.
        :param args: Arguments which are merged into msg using the string formatting operator.
        :param kwargs: Only one keyword argument is inspected: 'lvl', the logging level of the logger.
                       If not given, logging level will default to debug.
        """
        lvl = kwargs.pop("lvl", 10)
        base_logger.log(lvl, msg, *args, **kwargs)

    @staticmethod
    def notify(heading, message, icon="info", display_time=5000, sound=True):
        """
        Send a notification to kodi.

        :param str heading: Dialog heading label.
        :param str message: Dialog message label.
        :param str icon: (Optional) Icon to use. option are 'error', 'info', 'warning'. (default => 'info')
        :param int display_time: (Optional) Display_time in milliseconds to show dialog. (default => 5000)
        :param bool sound: (Optional) Whether or not to play notification sound. (default => True)
        """
        if isinstance(heading, unicode):
            heading = heading.encode("utf8")

        if isinstance(message, unicode):
            message = message.encode("utf8")

        # Send Error Message to Display
        dialog = xbmcgui.Dialog()
        dialog.notification(heading, message, icon, display_time, sound)

    @staticmethod
    def localize(string_id):
        """
        Returns an addon's localized 'unicode string'.

        :param int string_id: The id or reference string to be localized.

        :returns: Localized 'unicode string'.
        :rtype: unicode
        """
        if 30000 <= string_id <= 30999:
            return addon_data.getLocalizedString(string_id)
        elif 32000 <= string_id <= 32999:
            return script_data.getLocalizedString(string_id)
        else:
            return xbmc.getLocalizedString(string_id)

    @staticmethod
    def get_info(key, addon_id=None):
        """
        Returns the value of an addon property as a 'unicode string'.

        :param key: Id of the property to access.
        :param str addon_id: (Optional) Id of another addon to extract properties from.

        :return: Add-on property as a 'unicode string'.
        :rtype: unicode

        :raises RuntimeError: IF no add-on for given id was found.
        """
        # Check if we are extracting data from another add-on
        if addon_id:
            resp = xbmcaddon.Addon(addon_id).getAddonInfo(key)
        elif key == "path_global" or key == "profile_global":
            resp = script_data.getAddonInfo(key[:key.find("_")])
        else:
            resp = addon_data.getAddonInfo(key)

        # Check if path needs to be translated first
        if resp[:10] == "special://":
            resp = xbmc.translatePath(resp)

        # Convert property into unicode
        return unicode(resp, "utf8")

    @property
    def icon(self):
        """The add-on's icon image path."""
        return self.get_info("icon")

    @property
    def fanart(self):
        """The add-on's fanart image path."""
        return self.get_info("fanart")

    @property
    def profile(self):
        """The add-on's profile data directory path."""
        return self.get_info("profile")

    @property
    def path(self):
        """The add-on's directory path."""
        return self.get_info("path")
