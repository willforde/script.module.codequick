# Standard Library Imports
import unicodedata
import hashlib
import logging
import sys
import os
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

PY3 = sys.version_info >= (3, 0)
data_pipe = None

# Unicode Type object, unicode on python2 or str on python3
unicode_type = type(u"")

# Region settings. Used by xbmc.getRegion
region_settings = {"datelong": "%A, %d %B %Y", "dateshort": "%d/%m/%Y",
                   "time": "%H:%M:%S", "meridiem": "PM", "speedunit": "km/h"}

# Dict of supported media types that kodi is able to play. Used by xbmc.getSupportedMedia
supported_media = {"video": ".m4v|.3g2|.3gp|.nsv|.tp|.ts|.ty|.strm|.pls|.rm|.rmvb|.mpd|.m3u|.m3u8|.ifo|.mov|.qt|.divx"
                            "|.xvid|.bivx|.vob|.nrg|.img|.iso|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg"
                            "|.mp4|.mkv|.mk3d|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.rar|.001|.wpl|.zip|.vdr|.dvr"
                            "-ms|.xsp|.mts|.m2t|.m2ts|.evo|.ogv|.sdp|.avs|.rec|.url|.pxml|.vc1|.h264|.rcv|.rss|.mpls"
                            "|.webm|.bdmv|.wtv|.pvr|.disc",
                   "music": ".nsv|.m4a|.flac|.aac|.strm|.pls|.rm|.rma|.mpa|.wav|.wma|.ogg|.mp3|.mp2|.m3u|.gdm|.imf"
                            "|.m15|.sfx|.uni|.ac3|.dts|.cue|.aif|.aiff|.wpl|.ape|.mac|.mpc|.mp+|.mpp|.shn|.zip|.rar"
                            "|.wv|.dsp|.xsp|.xwav|.waa|.wvs|.wam|.gcm|.idsp|.mpdsp|.mss|.spt|.rsd|.sap|.cmc|.cmr|.dmc"
                            "|.mpt|.mpd|.rmt|.tmc|.tm8|.tm2|.oga|.url|.pxml|.tta|.rss|.wtv|.mka|.tak|.opus|.dff|.dsf"
                            "|.cdda",
                   "picture": ".png|.jpg|.jpeg|.bmp|.gif|.ico|.tif|.tiff|.tga|.pcx|.cbz|.zip|.cbr|.rar|.rss|.webp"
                              "|.jp2|.apng"}

# Kodi user directory
KODI_INSTALL_PATH = os.path.realpath("/usr/share/kodi")
KODI_SOURCE_PATH = os.path.join(KODI_INSTALL_PATH, "addons")
KODI_PROFILE_PATH = os.path.realpath("/home/willforde/.kodi")
KODI_ADDON_PATH = os.path.join(KODI_PROFILE_PATH, "addons")
KODI_TEMP_PATH = os.path.join(KODI_PROFILE_PATH, "temp")
KODI_DATA_PATH = os.path.join(KODI_PROFILE_PATH, "userdata", "addon_data")

# Kodi paths mapping. Used by xbmc.translatePath
path_map = {"home": KODI_PROFILE_PATH,
            "temp": KODI_TEMP_PATH,
            "profile": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "masterprofile": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "userdata": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "subtitles": KODI_TEMP_PATH,
            "database": os.path.join(KODI_PROFILE_PATH, "userdata", "Database"),
            "thumbnails": os.path.join(KODI_PROFILE_PATH, "userdata", "Thumbnails"),
            "musicplaylists": os.path.join(KODI_PROFILE_PATH, "userdata", "playlists", "music"),
            "videoplaylists": os.path.join(KODI_PROFILE_PATH, "userdata", "playlists", "video"),
            "recordings": KODI_TEMP_PATH,
            "screenshots": KODI_TEMP_PATH,
            "cdrips": KODI_TEMP_PATH,
            "xbmc": KODI_INSTALL_PATH,
            "logpath": os.path.join(KODI_TEMP_PATH, "kodi.log"),
            "skin": KODI_TEMP_PATH}

# Data store for addon. Use in xbmcplugin and xbmcgui
plugin_data = {"succeeded": False, "updatelisting": False, "resolved": None, "contenttype": None,  "category": None,
               "sortmethods": [], "playlist": [], "listitem": []}

# Base logger
logger = logging.getLogger("cli")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter("%(relativeCreated)-13s %(levelname)7s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def ensure_bytes(data):
    """
    Ensures that given string is returned as a UTF-8 encoded string.

    :param data: String to convert if needed.
    :returns: The given string as UTF-8.
    :rtype: bytes
    """
    return data if isinstance(data, bytes) else unicode_type(data).encode("utf8")


def ensure_native_str(data):
    """
    Ensures that given string is returned as a native str type, bytes on python2 or unicode on python3.

    :param data: String to convert if needed.
    :returns: The given string as UTF-8.
    :rtype: str
    """
    if isinstance(data, str):
        return data
    elif isinstance(data, unicode_type):
        # Only executes on python 2
        return data.encode("utf8")
    elif isinstance(data, bytes):
        # Only executes on python 3
        return data.decode("utf8")
    else:
        str(data)


def ensure_unicode(data):
    """
    Ensures that given string is return as a unicode string.

    :param data: String to convert if needed.
    :returns: The given string as unicode.
    :rtype: unicode
    """
    if isinstance(data, bytes):
        return data.decode("utf8")
    else:
        return unicode_type(data)


def safe_path(path):
    """
    Convert path into a encoding that best suits the platform os.
    Unicode when on windows, utf8 when on linux/bsd.

    :type path: bytes or unicode
    :param path: The path to convert.
    :return: Returns the path as unicode or utf8 encoded string.
    """
    # Ensure unicode if running windows
    if sys.platform.startswith("win"):
        return ensure_unicode(path)
    else:
        return ensure_bytes(path)


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


def handle_prompt(prompt):
    if data_pipe:
        data_pipe.send({"prompt": prompt})
        return data_pipe.recv()
    else:
        return input(prompt)
