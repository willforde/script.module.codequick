# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library Imports
import binascii
import logging
import inspect
import pickle
import time
import sys
import re

# Kodi imports
import xbmcaddon
import xbmcgui
import xbmc

# Package imports
from codequick.utils import parse_qs, ensure_native_str, urlparse

script_data = xbmcaddon.Addon("script.module.codequick")
addon_data = xbmcaddon.Addon()

plugin_id = addon_data.getAddonInfo("id")
logger_id = re.sub("[ .]", "-", addon_data.getAddonInfo("name"))

# Logger specific to this module
logger = logging.getLogger("%s.support" % logger_id)

# Listitem auto sort methods
auto_sort = set()


class LoggingMap(dict):
    def __init__(self):
        super(LoggingMap, self).__init__()
        self[10] = xbmc.LOGDEBUG    # logger.debug
        self[20] = xbmc.LOGNOTICE   # logger.info
        self[30] = xbmc.LOGWARNING  # logger.warning
        self[40] = xbmc.LOGERROR    # logger.error
        self[50] = xbmc.LOGFATAL    # logger.critical

    def __missing__(self, key):
        """Return log notice for any unexpected log level."""
        return xbmc.LOGNOTICE


class KodiLogHandler(logging.Handler):
    """
    Custom Logger Handler to forward logs to Kodi.

    Log records will automatically be converted from unicode to utf8 encoded strings.
    All debug messages will be stored locally and outputed as warning messages if a critical error occurred.
    This is done so that debug messages will appear on the normal kodi log file without having to enable debug logging.

    :ivar debug_msgs: Local store of degub messages.
    """
    def __init__(self):
        super(KodiLogHandler, self).__init__()
        self.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
        self.log_level_map = LoggingMap()
        self.debug_msgs = []

    def emit(self, record):
        """
        Forward the log record to kodi, lets kodi handle the logging.

        :param logging.LogRecord record: The log event record.
        """
        formatted_msg = ensure_native_str(self.format(record))
        log_level = record.levelno

        # Forward the log record to kodi with translated log level
        xbmc.log(formatted_msg, self.log_level_map[log_level])

        # Keep a history of all debug records so they can be logged later if a critical error occurred
        # Kodi by default, won't show debug messages unless debug logging is enabled
        if log_level == 10:
            self.debug_msgs.append(formatted_msg)

        # If a critical error occurred, log all debug messages as warnings
        elif log_level == 50 and self.debug_msgs:
            xbmc.log("###### debug ######", xbmc.LOGWARNING)
            for msg in self.debug_msgs:
                xbmc.log(msg, xbmc.LOGWARNING)
            xbmc.log("###### debug ######", xbmc.LOGWARNING)


class Route(object):
    """
    Handle callback route data.

    :param callback: The callable callback function.
    :param parent: The parent class that will handle the response from callback.
    :param str path: The route path to func/class.

    :ivar bool is_playable: True if callback is playable, else False.
    :ivar bool is_folder: True if callback is a folder, else False.
    :ivar decorated_callback: The decorated func/class.
    :ivar callback: The callable callback function.
    :ivar parent: The parent class that will handle the response from callback.
    :ivar str path: The route path to func/class.
    """
    __slots__ = ("parent", "callback", "decorated_callback", "path", "is_playable", "is_folder")

    def __init__(self, callback, parent, path):
        # Register a class callback
        if inspect.isclass(callback):
            if hasattr(callback, "run"):
                self.parent = parent = callback
                self.callback = callback.run
                callback.test = staticmethod(self.unittest_caller)
            else:
                raise NameError("missing required 'run' method for class: '{}'".format(callback.__name__))
        else:
            # Register a function callback
            self.parent = parent
            self.callback = callback
            callback.test = self.unittest_caller

        self.decorated_callback = callback
        self.is_playable = parent.is_playable
        self.is_folder = parent.is_folder
        self.path = path

    def args_to_kwargs(self, args, kwargs):
        """
        Convert positional arguments to keyword arguments and merge into callback parameters.

        :param tuple args: List of positional arguments to extract names for.
        :param dict kwargs: The dict of callback parameters that will be updated.
        :returns: A list of tuples consisting of ('arg name', 'arg value)'.
        :rtype: list
        """
        callback_args = self.arg_names()[1:]
        arg_map = zip(callback_args, args)
        kwargs.update(arg_map)

    def arg_names(self):
        """Return a list of argument names, positional and keyword arguments."""
        try:
            # noinspection PyUnresolvedReferences
            return inspect.getfullargspec(self.callback).args
        except AttributeError:
            # "inspect.getargspec" is deprecated in python 3
            return inspect.getargspec(self.callback).args

    def unittest_caller(self, *args, **kwargs):
        """
        Function to allow callbacks to be easily called from unittests.
        Parent argument will be auto instantiated and passed to callback.
        This basically acts as a constructor to callback.

        Test specific Keyword args:
        execute_delayed: Execute any registered delayed callbacks.

        :param args: Positional arguments to pass to callback.
        :param kwargs: Keyword arguments to pass to callback.
        :returns: The response from the callback function.
        """
        execute_delayed = kwargs.pop("execute_delayed", False)

        # Change the selector to match callback route been tested
        # This will ensure that the plugin paths are currect
        dispatcher.selector = self.path

        # Update support params with the params
        # that are to be passed to callback
        if args:
            self.args_to_kwargs(args, dispatcher.params)

        if kwargs:
            dispatcher.params.update(kwargs)

        # Instantiate the parent
        parent_ins = self.parent()

        try:
            # Now we are ready to call the callback function and return its results
            results = self.callback(parent_ins, *args, **kwargs)
            if inspect.isgenerator(results):
                results = list(results)

        except Exception:
            raise

        else:
            # Execute Delated callback functions if any
            if execute_delayed:
                dispatcher.run_delayed()

            return results

        finally:
            # Reset global datasets
            kodi_logger.debug_msgs = []
            dispatcher.reset()
            auto_sort.clear()


class Dispatcher(object):
    """Class to handle registering and dispatching of callback functions."""

    def __init__(self):
        self.registered_delayed = []
        self.registered_routes = {}

        # Extract arguments given by Kodi
        _, _, route, raw_params, _ = urlparse.urlsplit(sys.argv[0] + sys.argv[2])
        self.selector = route if len(route) > 1 else "root"

        if raw_params:
            self.params = params = parse_qs(raw_params)

            # Unpickle pickled data
            if "_pickle_" in params:
                unpickled = pickle.loads(binascii.unhexlify(params.pop("_pickle_")))
                params.update(unpickled)

            # Construct a separate dictionary for callback specific parameters
            self.callback_params = {key: value for key, value in params.items()
                                    if not (key.startswith(u"_") and key.endswith(u"_"))}
        else:
            self.callback_params = {}
            self.params = {}

    def reset(self):
        """Reset session parameters, this is needed for unittests to work properly."""
        self.registered_delayed[:] = []
        self.callback_params.clear()
        self.selector = "root"
        self.params.clear()

    def register(self, callback, parent):
        """
        Register route callback function

        :param callback: The callback function.
        :param parent: Parent class that will handle the callback, used when callback is a function.
        :returns: The callback function with extra attributes added, 'route', 'testcall'.
        """
        # Construct route path
        path = callback.__name__.lower()
        if path != "root":
            path = "/{}/{}".format(callback.__module__.strip("_").replace(".", "/"), callback.__name__).lower()

        # Register callback only if it's route path is unique
        if path in self.registered_routes:
            raise ValueError("encountered duplicate route: '{}'".format(path))
        else:
            self.registered_routes[path] = route = Route(callback, parent, path)
            callback.route = route
            return callback

    def register_delayed(self, func, args, kwargs):
        callback = (func, args, kwargs)
        self.registered_delayed.append(callback)

    def run(self):
        """Dispatch to selected route path."""

        logger.debug("Dispatching to route: '%s'", self.selector)
        logger.debug("Callback parameters: '%s'", self.callback_params)

        try:
            # Fetch the controling class and callback function/method
            route = self.registered_routes[self.selector]
            execute_time = time.time()

            # Initialize controller and execute callback
            parent_ins = route.parent()
            results = route.callback(parent_ins, **self.callback_params)
            if hasattr(parent_ins, "_process_results"):
                # noinspection PyProtectedMember
                parent_ins._process_results(results)

        except Exception as e:
            # Log the error in both the gui and the kodi log file
            dialog = xbmcgui.Dialog()
            dialog.notification(e.__class__.__name__, str(e), addon_data.getAddonInfo("icon"))
            logger.critical(str(e), exc_info=1)

        else:
            from . import start_time
            logger.debug("Route Execution Time: %ims", (time.time() - execute_time) * 1000)
            logger.debug("Total Execution Time: %ims", (time.time() - start_time) * 1000)
            self.run_delayed()

    def run_delayed(self):
        """Execute all callbacks, if any."""
        if self.registered_delayed:
            # Time before executing callbacks
            start_time = time.time()

            # Execute each callback one by one
            for func, args, kwargs in self.registered_delayed:
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logger.exception(str(e))

            # Log execution time of callbacks
            logger.debug("Callbacks Execution Time: %ims", (time.time() - start_time) * 1000)

    def get_route(self, path=None):
        """
        Return the given route object.
        
        :param str path: The route path to fetch the route object for.

        :returns: A callback route.
        :rtype: Route
        """
        return self.registered_routes[path if path else self.selector]


def build_path(callback=None, args=None, query=None, **extra_query):
    """
    Build addon url that can be passeed to kodi for kodi to use when calling listitems.

    :param callback: [opt] The route selector path referencing the callback object. (default => current route selector)
    :param tuple args: [opt] Positional arguments that will be add to plugin path.
    :param dict query: [opt] A set of query key/value pairs to add to plugin path.
    :param extra_query: [opt] Keyword arguments if given will be added to the current set of querys.

    :return: Plugin url for kodi.
    :rtype: str
    """

    # Set callback to current callback if not given
    route = callback.route if callback else dispatcher.get_route()

    # Convert args to keyword args if required
    if args:
        route.args_to_kwargs(args, query)

    # If extra querys are given then append the
    # extra querys to the current set of querys
    if extra_query:
        query = dispatcher.params.copy()
        query.update(extra_query)

    # Encode the query parameters using json
    if query:
        query = "_pickle_=" + ensure_native_str(binascii.hexlify(pickle.dumps(query, protocol=pickle.HIGHEST_PROTOCOL)))

    # Build kodi url with new path and query parameters
    return urlparse.urlunsplit(("plugin", plugin_id, route.path, query, ""))


# Setup kodi logging
kodi_logger = KodiLogHandler()
base_logger = logging.getLogger()
base_logger.addHandler(kodi_logger)
base_logger.setLevel(logging.DEBUG)
base_logger.propagate = False

# Dispatcher to manage route callbacks
dispatcher = Dispatcher()
run = dispatcher.run
