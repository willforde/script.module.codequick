"""
Copyright: (c) 2013 - 2016 William Forde (willforde+codequick@gmail.com)
License: GPLv3, see LICENSE for more details

codequick is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

codequick is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import time

# Start time of codequick
start_time = time.time()

# Standard Library Imports
import logging

# Kodi imports
import xbmc

# Shortcut variable for speedups.
kodi_log = xbmc.log

# Level mapper to convert logger levels to kodi logger levels
log_level_map = {10: xbmc.LOGWARNING,    # logger.debug xbmc.LOGDEBUG
                 20: xbmc.LOGNOTICE,   # logger.info
                 30: xbmc.LOGWARNING,  # logger.warning
                 40: xbmc.LOGERROR,    # logger.error
                 50: xbmc.LOGFATAL}    # logger.critical

# Logging Levels
CRITICAL = 50
WARNING = 30
ERROR = 40
DEBUG = 10
INFO = 20


class KodiLogHandler(logging.Handler):
    """Custom Logger Handler to forward logs to Kodi"""
    def __init__(self):
        super(KodiLogHandler, self).__init__()
        self.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
        self.debug_msgs = []

    def emit(self, record):
        """Forward the log record to kodi, lets kodi handle the logging"""
        log_level = record.levelno
        formatted_msg = self.format(record)
        if isinstance(formatted_msg, unicode):
            formatted_msg = formatted_msg.encode("utf8")

        # Forward the log record to kodi
        kodi_log(formatted_msg, log_level_map[log_level])

        # Keep a history of all debug records so they can be logged later if a critical error occurred
        # Kodi by default, won't show debug messages unless debug logging is enabled
        if log_level == 10:
            self.debug_msgs.append(formatted_msg)

        # If a critical error occurred, log all debug messages as warnings
        elif log_level == 50 and False:
            kodi_log("###### debug ######", xbmc.LOGWARNING)
            for msg in self.debug_msgs:
                kodi_log(msg, xbmc.LOGWARNING)
            kodi_log("###### debug ######", xbmc.LOGWARNING)

# Logging
logger = logging.getLogger("codequick")
logger.addHandler(KodiLogHandler())
logger.propagate = False
logger.setLevel(DEBUG)

# Package imports
from .api import Script, VirtualFS, PlayMedia, script, route, resolve, run
from .storage import PersistentDict, PersistentList, PersistentSet

__all__ = ["script", "route", "resolve", "run", "PersistentDict", "PersistentList", "PersistentSet"]
