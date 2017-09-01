"""
Offers classes and functions that provide information about the media currently
playing and that allow manipulation of the media player (such as starting a new song).
You can also find system information using the functions available in this library.
"""

# Standard Library Imports
import logging
import random
import time
import os
import re

# Other imports
import xbmcgui as _xbmcgui
from codequickcli.addondb import db as addon_db
import codequickcli.support as _support

__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:03 BST 2015'
__platform__ = 'ALL'
__version__ = '2.25.0'

abortRequested = False
CAPTURE_FLAG_CONTINUOUS = 1
CAPTURE_FLAG_IMMEDIATELY = 2
CAPTURE_STATE_DONE = 3
CAPTURE_STATE_FAILED = 4
CAPTURE_STATE_WORKING = 0
DRIVE_NOT_READY = 1
ENGLISH_NAME = 2
ISO_639_1 = 0
ISO_639_2 = 1
LOGDEBUG = 0
LOGERROR = 4
LOGFATAL = 6
LOGINFO = 1
LOGNONE = 7
LOGNOTICE = 2
LOGSEVERE = 5
LOGWARNING = 3
PLAYER_CORE_AUTO = 0
PLAYER_CORE_DVDPLAYER = 1
PLAYER_CORE_MPLAYER = 2
PLAYER_CORE_PAPLAYER = 3
PLAYLIST_MUSIC = 0
PLAYLIST_VIDEO = 1
SERVER_AIRPLAYSERVER = 2
SERVER_EVENTSERVER = 6
SERVER_JSONRPCSERVER = 3
SERVER_UPNPRENDERER = 4
SERVER_UPNPSERVER = 5
SERVER_WEBSERVER = 1
SERVER_ZEROCONF = 7
TRAY_CLOSED_MEDIA_PRESENT = 96
TRAY_CLOSED_NO_MEDIA = 64
TRAY_OPEN = 16

# Kodi log levels
log_levels = (logging.DEBUG,  # xbmc.LOGDEBUG
              logging.DEBUG,  # xbmc.LOGINFO
              logging.INFO,  # xbmc.LOGNOTICE
              logging.WARNING,  # xbmc.LOGWARNING
              logging.ERROR,  # xbmc.LOGERROR
              logging.CRITICAL,  # xbmc.LOGSEVERE
              logging.CRITICAL,  # xbmc.LOGFATAL
              logging.DEBUG)  # xbmc.LOGNONE


def audioResume():
    """
    Resume Audio engine.

    example::

        xbmc.audioResume()
    """
    pass


def audioSuspend():
    """
    Suspend Audio engine.

    example::

        xbmc.audioSuspend()
    """
    pass


# noinspection PyUnusedLocal, PyShadowingBuiltins
def convertLanguage(language, format):
    """
    Returns the given language converted to the given format as a string.

    :param str language: string either as name in English, two letter code (ISO 639-1),
                         or three letter code (ISO 639-2/T(B)
    :param str format: format of the returned language string:

    - ``xbmc.ISO_639_1``: two letter code as defined in ISO 639-1
    - ``xbmc.ISO_639_2``: three letter code as defined in ISO 639-2/T or ISO 639-2/B
    - ``xbmc.ENGLISH_NAME``: full language name in English (default)

    :returns: Converted Language string
    :rtype: str

    example::

        language = xbmc.convertLanguage(English, xbmc.ISO_639_2)
    """
    raise NotImplementedError


# noinspection PyUnusedLocal
def enableNavSounds(yesNo):
    """
    Enables/Disables nav sounds

    :param bool yesNo: enable (``True``) or disable (``False``) nav sounds

    example::

        xbmc.enableNavSounds(True)
    """
    pass


# noinspection PyUnusedLocal, PyShadowingBuiltins
def executebuiltin(function):
    """
    Execute a built in XBMC function.

    :param str function: string - builtin function to execute.

    List of functions: http://kodi.wiki/?title=List_of_Built_In_Functions

    example::

        xbmc.executebuiltin('XBMC.RunXBE(c:\avalaunch.xbe)')
    """
    pass


# noinspection PyUnusedLocal
def executeJSONRPC(jsonrpccommand):
    """
    Execute an JSONRPC command.

    :param str jsonrpccommand: string - jsonrpc command to execute.
    :returns: jsonrpc return string
    :rtype: str

    List of commands: http://kodi.wiki/?title=JSON-RPC_API

    example::

        response = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "id": 1 }')
    """
    return str()


# noinspection PyUnusedLocal
def executescript(script):
    """
    Execute a python script.

    :param str script: string - script filename to execute.

    example::

        xbmc.executescript('special://home/scripts/add.py')
    """
    pass


# noinspection PyUnusedLocal
def getCacheThumbName(path):
    """
    Get thumb cache filename.

    :param path: string or unicode -- path to file
    :type path: str or unicode

    :returns: Thumb cache filename
    :rtype: str

    Example::

        thumb = xbmc.getCacheThumbName('f:\videos\movie.avi')
    """
    raise NotImplementedError


def getCleanMovieTitle(path, usefoldername=False):
    """
    Get clean movie title and year string if available.

    :type path: str or unicode
    :param path: string or unicode - String to clean
    :param bool usefoldername: [opt] bool - use folder names (defaults to ``False``)

    :returns: Clean movie title and year string if available.
    :rtype: str

    example::

        'file', '' = xbmc.getCleanMovieTitle('/kodi_path/to/moviefolder/file.mkv')
        'file', '2017' = xbmc.getCleanMovieTitle('/kodi_path/to/moviefolder/file (2017).mkv')
        'topgun', '' = xbmc.getCleanMovieTitle('/kodi_path/to/topgun/file.mkv', True)
        'topgun', '2017' = xbmc.getCleanMovieTitle('/kodi_path/to/topgun (2017)/file.mkv', True)
    """
    path = _support.ensure_native_str(path)
    directory, title = os.path.split(path)
    if usefoldername:
        title = os.path.basename(directory)

    year = re.search('\((\d\d\d\d)\)', title)
    if year:
        title = title.replace(year.group(), "")
        year = year.group(1)
    else:
        year = ""

    return title.rsplit(".", 1)[0].strip(), year


# noinspection PyUnusedLocal
def getCondVisibility(condition):
    """
    Get visibility conditions.

    :param str condition: string - condition to check.
    :returns: ``True`` (1) or ``False`` (0) as a bool
    :rtype: bool

    List of Conditions - http://kodi.wiki/view/List_of_Boolean_Conditions

    .. note:: You can combine two (or more) of the above settings by using "+" as an ``AND`` operator,
              "|" as an ``OR`` operator, "!" as a ``NOT`` operator, and "[" and "]" to bracket expressions.

    example::

        visible = xbmc.getCondVisibility('[Control.IsVisible(41) + !Control.IsVisible(12)]')
    """
    raise NotImplementedError


def getDVDState():
    """
    Get the dvd state as an integer.

    :returns: Returns the dvd state as an integer.
    :rtype: int

    return values are:

    - 1 : ``xbmc.DRIVE_NOT_READY``
    - 16 : ``xbmc.TRAY_OPEN``
    - 64 : ``xbmc.TRAY_CLOSED_NO_MEDIA``
    - 96 : ``xbmc.TRAY_CLOSED_MEDIA_PRESENT``

    example::

        dvdstate = xbmc.getDVDState()
    """
    return TRAY_CLOSED_NO_MEDIA


def getFreeMem():
    """
    Get amount of free memory in MB.

    :returns: The amount of free memory in MB as an integer
    :rtype: int

    example::

        freemem = xbmc.getFreeMem()
    """
    return 1024


def getGlobalIdleTime():
    """
    Get the elapsed idle time in seconds.

    :returns: Elapsed idle time in seconds as an integer
    :rtype: long

    example::

        t = xbmc.getGlobalIdleTime()
    """
    return _support.long_type()


# noinspection PyUnusedLocal
def getInfoImage(infotag):
    """
    Get filename including path to the InfoImage's thumbnail.

    :param str infotag: string - infotag for value you want returned.
    :returns: Filename including path to the InfoImage's thumbnail as a string.
    :rtype: str

    List of InfoTags - http://kodi.wiki/view/InfoLabels

    example::

        filename = xbmc.getInfoImage('Weather.Conditions')
    """
    raise NotImplementedError


# noinspection PyUnusedLocal
def getInfoLabel(cLine):
    """
    Get a info label.

    :param str cLine: string - infoTag for value you want returned.
    :returns: InfoLabel as a string.
    :rtype: str

    List of InfoTags - http://kodi.wiki/view/InfoLabels

    example::

        label = xbmc.getInfoLabel('Weather.Conditions')
    """
    raise NotImplementedError


def getIPAddress():
    """
    Get the current ip address.

    :returns: The current ip address as a string.
    :rtype: str

    example::

        ip = xbmc.getIPAddress()
    """
    return "127.0.0.1"


# noinspection PyUnusedLocal, PyShadowingBuiltins
def getLanguage(format=ENGLISH_NAME, region=False):
    """
    Get the active language.

    :param int format: [opt] format of the returned language string

    - xbmc.ISO_639_1: two letter code as defined in ISO 639-1
    - xbmc.ISO_639_2: three letter code as defined in ISO 639-2/T or ISO 639-2/B
    - xbmc.ENGLISH_NAME: full language name in English (default)

    :param bool region: [opt] append the region delimited by "-" of the language (setting)
                        to the returned language string.

    :returns: The active language as a string.
    :rtype: str

    example::

        language = xbmc.getLanguage(xbmc.ENGLISH_NAME)
    """
    if format == ISO_639_1:
        lang = "en"
    elif format == ISO_639_2:
        lang = "eng"
    else:
        lang = "english"

    if region:
        return "{}-GB".format(lang)
    else:
        return lang


def getLocalizedString(id):
    """
    Returns an addon's localize 'unicode string'.

    :param int id: string - id# for string you want to localize.
    :returns: Localized 'unicode string'
    :rtype: unicode

    .. note: See strings.po in \language\{yourlanguage}\ for which id you need for a string.

    Example::

        locstr = xbmc.getLocalizedString(6)
    """
    string = addon_db["resource.language.en_gb"].strings[id].decode("utf8")
    return string.decode("utf8") if isinstance(string, bytes) else string


# noinspection PyShadowingBuiltins
def getRegion(id):
    """
    Returns your regions setting as a string for the specified id.

    :param str id: string - id of setting to return

    :returns: Region setting
    :rtype: str

    You can use the above as keywords for arguments

    .. note:: choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)

    example::

        date_long_format = xbmc.getRegion('datelong')
    """
    return _support.region_settings[id]


def getSkinDir():
    """
    Get the active skin directory.

    :returns: The active skin directory as a string.
    :rtype: str

    .. note:: This is not the full path like 'special://home/addons/skin.estuary', but only 'skin.estuary'.

    example::

        skindir = xbmc.getSkinDir()
    """
    return "skin.estuary"


def getSupportedMedia(mediaType):
    """
    Get the supported file types for the specific media.

    :param str mediaType: string - media type

    :returns: Supported file types for the specific media as a string
    :rtype: str

    You can use the above as keywords for arguments.

    .. note:: media type can be (video, music, picture).
              The return value is a pipe separated string of filetypes (eg. '.mov|.avi').

    example::

        mTypes = xbmc.getSupportedMedia('video')
    """
    return _support.supported_media[mediaType]


def getUserAgent():
    """
    Returns Kodi's HTTP UserAgent string

    :returns: HTTP user agent
    :rtype: str

    Example::

        xbmc.getUserAgent()
    """
    return "Kodi/17.0-ALPHA1 (X11; Linux x86_64) Ubuntu/15.10 App_Bitness/64 " \
           "Version/17.0-ALPHA1-Git:2015-12-23-5770d28"


def log(msg, level=LOGDEBUG):
    """
    Write a string to XBMC's log file and the debug window.

    :param str msg: string - text to output.
    :param int level: [opt] integer - log level to ouput at. (default=``LOGDEBUG``)

    - xbmc.LOGDEBUG    In depth information about the status of Kodi. This information can pretty much only
                       be deciphered by a developer or long time Kodi power user.
    - xbmc.LOGINFO     Something has happened. It's not a problem, we just thought you might want to know.
                       Fairly excessive output that most people won't care about.
    - xbmc.LOGNOTICE   Similar to INFO but the average Joe might want to know about these events.
                       This level and above are logged by default.
    - xbmc.LOGWARNING  Something potentially bad has happened. If Kodi did something you didn't expect,
                       this is probably why. Watch for errors to follow.
    - xbmc.LOGERROR    This event is bad. Something has failed. You likely noticed problems with the
                       application be it skin artifacts, failure of playback a crash, etc.
    - xbmc.LOGFATAL    We're screwed. Kodi is about to crash.

    .. note:: You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.

    Example::

        xbmc.log('This is a test string.', level=xbmc.LOGDEBUG)
    """
    _support.logger.log(log_levels[level], msg)


def makeLegalFilename(filename, fatX=True):
    """
    Returns a legal filename or path as a string.

    :param filename: string or unicode -- filename/path to make legal
    :type filename: str or unicode

    :param bool fatX: [opt] bool -- ``True`` = Xbox file system(Default)

    :returns: Legal filename or path as a string
    :rtype: str

    .. note: If fatX is ``True`` you should pass a full path.
             If fatX is ``False`` only pass the basename of the path.

    .. note: You can use the above as keywords for arguments and skip certain optional arguments.
             Once you use a keyword, all following arguments require the keyword.

    Example::

        filename = xbmc.makeLegalFilename('F: Age: The Meltdown.avi')
    """
    filename = _support.ensure_native_str(filename)
    if fatX:
        path, filename = os.path.split(filename)
        return os.path.join(path, _support.normalize_filename(filename))
    else:
        return _support.normalize_filename(filename)


# noinspection PyUnusedLocal
def playSFX(filename, useCached=True):
    """
    Plays a wav file by filename.

    :param str filename: string - filename of the wav file to play.
    :param bool useCached: [opt] bool - False = Dump any previously cached wav associated with filename.

    example::

        xbmc.playSFX('special://xbmc/scripts/dingdong.wav')
        xbmc.playSFX('special://xbmc/scripts/dingdong.wav',False)
    """
    pass


def restart():
    """
    Restart the htpc.

    example::

        xbmc.restart()
    """
    pass


def shutdown():
    """
    Shutdown the htpc.

    example::

        xbmc.shutdown()
    """
    pass


# noinspection PyUnusedLocal
def skinHasImage(image):
    """
    Check skin for presence of Image.

    :param str image: string - image filename
    :returns: True if the image file exists in the skin
    :rtype: bool

    .. note:: If the media resides in a subfolder include it.
        (eg. home-myfiles\home-myfiles2.png).

        You can use the above as keywords for arguments.

    example::

        exists = xbmc.skinHasImage('ButtonFocusedTexture.png')
    """
    return True


def sleep(timemillis):
    """
    Sleeps for 'time' msec.

    :param int timemillis: integer - number of msec to sleep.

    .. note: This is useful if you have for example aPlayer class that is waiting
             for onPlayBackEnded() calls.

    :raises TypeError: if time is not an integer.

    Example::

        xbmc.sleep(2000) # sleeps for 2 seconds
    """
    if isinstance(timemillis, int):
        time.sleep(float(timemillis) / 1000)
    else:
        raise TypeError("Time intervile of type '%s' is not of valid type int" % type(timemillis))


# noinspection PyUnusedLocal
def startServer(iTyp, bStart, bWait=False):
    """
    start or stop a server.

    :param int iTyp: integer -- use SERVER_* constants
    :param bool bStart: bool -- start (True) or stop (False) a server
    :param bool bWait : [opt] bool -- wait on stop before returning (not supported by all servers)

    :return: bool -- ``True`` or ``False``
    :rtype: bool

    Example::

        xbmc.startServer(xbmc.SERVER_AIRPLAYSERVER, False)
    """
    pass


def stopSFX():
    """
    Stops wav file.

    example::

        xbmc.stopSFX()
    """
    pass


def translatePath(path):
    """
    Returns the translated path.

    :param path: string or unicode - Path to format
    :type path: str or unicode

    :returns: Translated path
    :rtype: str

    .. note: Only useful if you are coding for both Linux and Windows.

    Converts ``'special://masterprofile/script_data'`` -> ``'/home/user/XBMC/UserData/script_data'`` on Linux.

    List of Special protocols - http://kodi.wiki/view/Special_protocol

    Example::

        fpath = xbmc.translatePath('special://masterprofile/script_data')
    """
    path = _support.ensure_native_str(path)
    # Return the path unmodified if not a special path
    if not path.startswith("special://"):
        return path

    # Extract the directory name
    special_path, path = path.split("/", 3)[2:]

    # Fetch realpath from the path mapper
    realpath = _support.path_map.get(special_path)
    if realpath is None:
        raise ValueError("%s is not a valid root dir." % special_path)
    else:
        return os.path.join(realpath, *path.split("/"))


def validatePath(path):
    """
    Returns the validated path.

    :param path: string or unicode - Path to format
    :type path: str or unicode

    :returns: Validated path
    :rtype: str

    .. note:: Only useful if you are coding for both Linux and Windows for fixing slash problems.
        e.g. Corrects 'Z:\\something/with\\mix/path' -> 'Z:\something\with\mix\path'

    Example::

        fpath = xbmc.validatePath('Z:\\something/with\\mix/path')
    """
    path = _support.ensure_native_str(path)
    alt_sep = "\\" if os.sep == "/" else "/"
    return path.replace(alt_sep, os.sep)


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class Keyboard(object):
    """
    Creates a new Keyboard object with default text heading and hidden input flag if supplied.

    :param str default: [opt] string - default text entry.
    :param str heading: [opt] string - keyboard heading.
    :param bool hidden: [opt] boolean - True for hidden text entry.

    Example::

        kb = xbmc.Keyboard('default', 'heading', True)
        kb.setDefault('password') # optional
        kb.setHeading('Enter password') # optional
        kb.setHiddenInput(True) # optional
        kb.doModal()
        if (kb.isConfirmed()):
            text = kb.getText()
    """

    def __init__(self, default="", heading="", hidden=False):
        self._heading = heading
        self._default = default
        self._hidden = hidden

        self._confirmed = False
        self._input = None

    def doModal(self, autoclose=0):
        """
        Show keyboard and wait for user action.

        :param int autoclose: [opt] integer - milliseconds to autoclose dialog.

        .. note::
            autoclose = 0 - This disables autoclose

        Example::

            kb.doModal(30000)
        """
        self._confirmed = True
        dialog = _xbmcgui.Dialog()
        self._input = dialog.input(self._heading, self._default,
                                   option=_xbmcgui.ALPHANUM_HIDE_INPUT if self._hidden else 0)

    def setDefault(self, default):
        """
        Set the default text entry.

        :param str default: string - default text entry.

        Example::

            kb.setDefault('password')
        """
        self._default = default

    def setHiddenInput(self, hidden):
        """
        Allows hidden text entry.

        :param bool hidden: boolean - ``True`` for hidden text entry.

        Example::

            kb.setHiddenInput(True)
        """
        self._hidden = hidden

    def setHeading(self, heading):
        """
        Set the keyboard heading.

        :param str heading: string - keyboard heading.

        Example::

            kb.setHeading('Enter password')
        """
        self._heading = heading

    def getText(self):
        """
        Returns the user input as a string.

        :return: entered text
        :rtype: str

        .. note::
            This will always return the text entry even if you cancel the keyboard.
            Use the isConfirmed() method to check if user cancelled the keyboard.
        """
        return self._input

    def isConfirmed(self):
        """
        Returns ``False`` if the user cancelled the input.

        :return: confirmed status
        :rtype: bool

        example::

            if (kb.isConfirmed()):
                pass
        """
        return self._confirmed


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class Player(object):
    """
    Player()

    Creates a new Player with as default the xbmc music playlist.

    .. note:: currently Player class constructor does not take any parameters.
              Kodi automatically selects a necessary player.
    """

    def __init__(self):
        pass

    def play(self, item=None, listitem=None, windowed=False, startpos=-1):
        """
        Play this item.

        :param str item: [opt] string - filename, url or playlist.
        :param listitem: [opt] listitem - used with setInfo() to set different infolabels.
        :type listitem: _xbmcgui.ListItem

        :param bool windowed: [opt] bool - true=play video windowed, false=play users preference.(default)
        :param int startpos: [opt] int - starting position when playing a playlist. Default = -1

        .. note:: If item is not given then the Player will try to play the current item
            in the current playlist.

            You can use the above as keywords for arguments and skip certain optional arguments.
            Once you use a keyword, all following arguments require the keyword.

        example::

            listitem = xbmcgui.ListItem('Ironman')
            listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
            xbmc.Player().play(url, listitem, windowed)
            xbmc.Player().play(playlist, listitem, windowed, startpos)
        """
        pass

    def stop(self):
        """Stop playing."""
        pass

    def pause(self):
        """Pause or resume playing if already paused."""
        pass

    def playnext(self):
        """Play next item in playlist."""
        pass

    def playprevious(self):
        """Play previous item in playlist."""
        pass

    def playselected(self, selected):
        """
        Play a certain item from the current playlist.

        :param int selected: Integer - Item to select
        """
        pass

    def onPlayBackStarted(self):
        """Will be called when xbmc starts playing a file."""
        pass

    def onPlayBackEnded(self):
        """Will be called when xbmc stops playing a file."""
        pass

    def onPlayBackStopped(self):
        """Will be called when user stops xbmc playing a file."""

    def onPlayBackPaused(self):
        """Will be called when user pauses a playing file."""
        pass

    def onPlayBackResumed(self):
        """Will be called when user resumes a paused file."""
        pass

    # noinspection PyShadowingNames
    def onPlayBackSeek(self, time, seekOffset):
        """
        Will be called when user seeks to a time.

        :param int time: integer - Time to seek to
        :param int seekOffset: integer - ?.
        """
        pass

    def onPlayBackSeekChapter(self, chapter):
        """
        Will be called when user performs a chapter seek.

        :param int chapter: integer - chapter to seek to.
        """
        pass

    def onPlayBackSpeedChanged(self, speed):
        """
        Will be called when players speed changes (eg. user FF/RW).

        :param int speed: integer - current speed of player.

        .. note:: negative speed means player is rewinding, 1 is normal playback speed.
        """
        pass

    def onQueueNextItem(self):
        """Will be called when player requests next item"""
        pass

    def isPlaying(self):
        """
        Check if Kodi is playing something.

        :returns: ``True`` if Kodi is playing a file, else ``False``
        :rtype: bool
        """
        return True

    def isPlayingAudio(self):
        """
        Check if kodi is playing audio.

        :returns: ``True`` if Kodi is playing a audio file, else ``False``
        :rtype: bool
        """
        return True

    def isPlayingVideo(self):
        """
        Check if kodi is playing video.

        :returns: ``True`` if Kodi is playing a video, else ``False``
        :rtype: bool
        """
        return True

    def isPlayingRDS(self):
        """
        Check for playing radio data system (RDS).

        :returns: ``True`` if kodi is playing a radio data system (RDS).
        :rtype: bool
        """

    def getPlayingFile(self):
        """
        Returns the current playing file as a string.

        .. note:: For LiveTV, returns a pvr:// url which is not translatable to an OS specific file or external url

        :returns: Playing filename
        :rtype: str

        :raises Exception: if player is not playing a file.
        """
        return str()

    def getVideoInfoTag(self):
        """
        Returns the VideoInfoTag of the current playing Movie.

        :returns: Video info tag
        :rtype: InfoTagVideo

        :raises Exception: If player is not playing a file or current file is not a movie file.

        .. note:: This doesn't work yet, it's not tested.
        """
        return InfoTagVideo()

    def getMusicInfoTag(self):
        """
        Returns the MusicInfoTag of the current playing 'Song'.

        :returns: Music info tag
        :rtype: InfoTagMusic

        :raises Exception: If player is not playing a file or current file is not a music file.
        """
        return InfoTagMusic()

    def getRadioRDSInfoTag(self):
        """
        Returns the RadioRDSInfoTag of the current playing 'Radio Song if. present'.

        :return: Radio RDS info tag
        :rtype: InfoTagRadioRDS

        :raises Exception: If player is not playing a file or current file is not a rds file.
        """
        return InfoTagRadioRDS()

    def getTotalTime(self):
        """
        Returns the total time of the current playing media in seconds.
        This is only accurate to the full second.

        :returns: Total time of the current playing media.
        :rtype: float

        :raises Exception: If player is not playing a file.
        """
        return float()

    def getTime(self):
        """
        Returns the current time of the current playing media as fractional seconds.

        :returns: Current time as fractional seconds
        :rtype: float

        :raises Exception: If player is not playing a file.
        """
        return float()

    def seekTime(self, seekTime):
        """
        Seeks the specified amount of time as fractional seconds.
        The time specified is relative to the beginning of the currently. playing media file.

        :param float seekTime: Time to seek as fractional seconds

        :raises Exception: If player is not playing a file.
        """
        pass

    def setSubtitles(self, subtitleFile):
        """
        Set subtitle file and enable subtitles.

        :param subtitleFile: string or unicode - File to use as source of subtitles
        :type subtitleFile: str or unicode

        Example::

            setSubtitles('/path/to/subtitle/test.srt')
        """
        pass

    def getSubtitles(self):
        """
        Get subtitle stream name.

        :returns: Stream name.
        :rtype: str
        """
        return str()

    def getAvailableAudioStreams(self):
        """
        Get audio stream names.

        :returns: List of audio streams as name.
        :rtype: list
        """
        return list()

    def getAvailableVideoStreams(self):
        """
        Get Video stream names

        :return: List of video streams as name
        :rtype: list
        """
        return list()

    def getAvailableSubtitleStreams(self):
        """
        Get Subtitle stream names

        :returns: List of subtitle streams as name.
        :rtype: list
        """
        return list()

    def setAudioStream(self, stream):
        """
        Set audio stream.

        :param int stream: int - Audio stream to select for play.
        """
        pass

    def setVideoStream(self, stream):
        """
        Set Video Stream.

        :param int stream: int - Video stream to select for play.
        """
        pass

    def setSubtitleStream(self, stream):
        """
        set Subtitle Stream

        :param int stream: int - Subtitle stream to select for play.

        example::

            setSubtitleStream(1)
        """
        pass

    def showSubtitles(self, bVisible):
        """
        enable/disable subtitles

        :param bool bVisible: boolean - ``True`` for visible subtitles.

        example::

            xbmc.Player().showSubtitles(True)
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class PlayList(object):
    """Retrieve a reference from a valid xbmc playlist

    :param int playlist: [opt] int - can be one of the next values. (default='xbmc.PLAYLIST_VIDEO')

    Options::

        0: xbmc.PLAYLIST_MUSIC
        1: xbmc.PLAYLIST_VIDEO

    Use PlayList[int position] or __getitem__(int position) to get a PlayListItem.
    """
    playlistItems = []

    def __init__(self, playlist=PLAYLIST_VIDEO):
        pass

    def __getitem__(self, item):
        """
        x.__getitem__(y) <==> x[y]
        :rtype: ListItem
        """
        return _support.plugin_data["playlist"][item]

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return len(_support.plugin_data["playlist"])

    def add(self, url, listitem=None, index=-1):
        """Adds a new file to the playlist.

        :type url: str or unicode
        :param url: string or unicode - filename or url to add.
        :param listitem: [opt] listitem - used with setInfo() to set different infolabels.
        :param int index: [opt] integer - position to add playlist item.

        Example::

            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            video = 'F:\\movies\\Ironman.mov'
            listitem = xbmcgui.ListItem('Ironman', thumbnailImage='F:\\movies\\Ironman.tbn')
            listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
            playlist.add(url=video, listitem=listitem, index=7)
        """
        if listitem is None:
            listitem = _xbmcgui.ListItem()
        listitem.setPath(url)

        if index:
            self.playlistItems.insert(index, listitem)
            _support.plugin_data["playlist"].insert(index, listitem)
        else:
            self.playlistItems.append(listitem)
            _support.plugin_data["playlist"].append(listitem)

    def load(self, filename):
        """
        Load a playlist.

        Clear current playlist and copy items from the file to this Playlist.
        filename can be like .pls or .m3u ...

        :param filename:
        :return: ``False`` if unable to load playlist, True otherwise.
        """
        raise NotImplementedError("'load' method of object '%s' is not Implemented" % type(self))

    def remove(self, filename):
        """
        Remove an item with this filename from the playlist.

        :param str filename: filename within the playlist.
        """
        pass

    def clear(self):
        """Clear all items in the playlist."""
        _support.plugin_data["playlist"] = []
        self.playlistItems = []

    def shuffle(self):
        """Shuffle the playlist."""
        random.shuffle(_support.plugin_data["playlist"])

    def unshuffle(self):
        """Unshuffle the playlist."""
        _support.plugin_data["playlist"] = self.playlistItems

    def size(self):
        """Returns the total number of PlayListItems in this playlist."""
        return len(self)

    def getposition(self):
        """
        Returns the position of the current song in this playlist.

        :returns: Position of the current song.
        :rtype: int
        """
        return 0

    def getPlayListId(self):
        """
        getPlayListId() --returns an integer.

        :returns: Id as an integer.
        :rtype: int
        """
        return 0


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class InfoTagMusic(object):
    """
    To get music info tag data of currently played source.

    .. note: Info tag load is only be possible from present player class.

    example::

        tag = xbmc.Player().getMusicInfoTag()
        title = tag.getTitle()
        url   = tag.getURL()
    """

    def getAlbum(self):
        """
        Returns the album from music tag as string if present.

        :return: [string] Music album name
        :rtype: str
        """
        return str()

    def getAlbumArtist(self):
        """
        Returns the album artist from music tag as string if present.

        :return: [string] Music album artist name
        :rtype: str
        """
        return str()

    def getArtist(self):
        """
        Returns the artist from music as string if present.

        :return: [string] Music artist
        :rtype: str
        """
        return str()

    def getComment(self):
        """
        Returns comment as string from music info tag.

        :return: [string] Comment on tag
        :rtype: str
        """
        return str()

    def getDbId(self):
        """
        Get identification number of tag in database.

        :return: [integer] database id.
        :rtype: int
        """
        return int()

    def getDisc(self):
        """
        Returns the disk number (if present) from music info tag as integer.

        :return: [integer] Disc number
        :rtype: int
        """
        return int()

    def getDuration(self):
        """
        Returns the duration of music as integer from info tag.

        :return: [integer] Duration
        :rtype: int
        """
        return int()

    def getGenre(self):
        """
        Returns the genre name from music tag as string if present.

        :return: [string] Genre name
        :rtype: str
        """
        return str()

    def getLastPlayed(self):
        """
        Returns last played time as string from music info tag.

        :return: [string] Last played date / time on tag
        :rtype: str
        """
        return str()

    def getListeners(self):
        """
        Returns the listeners as integer from music info tag.

        :return: [integer] Listeners
        :rtype: int
        """
        return int()

    def getLyrics(self):
        """
        Returns a string from lyrics.

        :return: [string] Lyrics on tag
        :rtype: str
        """
        return str()

    def getMediaType(self):
        """
        Get the media type of the music item.

        :return: [string] media type
        :rtype: str

        Available strings about media type for music::

            artist 	If it is defined as an artist
            album 	If it is defined as an album
            song 	If it is defined as a song
        """
        return str()

    def getPlayCount(self):
        """
        Returns the number of carried out playbacks.

        :return: [integer] Playback count
        :rtype: int
        """
        return int()

    def getRating(self):
        """
        Returns the scraped rating as integer.

        :return: [integer] Rating
        :rtype: int
        """
        return int()

    def getReleaseDate(self):
        """
        Returns the release date as string from music info tag (if present).

        :return: [string] Release date
        :rtype: str
        """
        return str()

    def getTitle(self):
        """
        Returns the title from music as string on info tag.

        :return: [string] Music title
        :rtype: str
        """
        return str()

    def getTrack(self):
        """
        Returns the track number (if present) from music info tag as integer.

        :return: [integer] Track number
        :rtype: int
        """
        return int()

    def getURL(self):
        """
        Returns url of source as string from music info tag.

        :return: [string] Url of source
        :rtype: str
        """
        return str()

    def getUserRating(self):
        """
        Returns the user rating as integer (-1 if not existing)

        :return: [integer] User rating
        :rtype: int
        """
        return int()


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class InfoTagVideo(object):
    """
    To get video info tag data of currently played source.

    .. note: Info tag load is only be possible from present player class.

    example::

        tag = xbmc.Player().getVideoInfoTag()
        title = tag.getTitle()
        file  = tag.getFile()
    """

    def getCast(self):
        """
        To get the cast of the video when available.

        :return: [string] Video casts
        :rtype str
        """
        return str()

    def getDbId(self):
        """
        Get identification number of tag in database.

        :return: [integer] database id
        :rtype: int
        """
        return int()

    def getDirector(self):
        """
        Get film director who has made the film (if present).

        :return: [string] Film director name.
        :rtype: str
        """
        return str()

    def getEpisode(self):
        """
        To get episode number of a series.

        :return: [integer] episode number
        :rtype: int
        """
        return int()

    def getFile(self):
        """
        To get the video file name.

        :return: [string] File name
        :rtype: str
        """
        return str()

    def getFirstAired(self):
        """
        Returns first aired date as string from info tag.

        :return: [string] First aired date
        :rtype: str
        """
        return str()

    def getGenre(self):
        """
        To get the Video Genre if available.

        :return: [string] Genre name
        :rtype: str
        """
        return str()

    def getIMDBNumber(self):
        """
        To get the IMDb number of the video (if present).

        :return: [string] IMDb number
        :rtype: str
        """
        return str()

    def getLastPlayed(self):
        """
        Get the last played date / time as string.

        :return: [string] Last played date / time
        :rtype: str
        """
        return str()

    def getMediaType(self):
        """
        Get the media type of the video.

        :return: [string] media type
        :rtype: str

        Available strings about media type for video::

            video 	    For normal video
            set 	    For a selection of video
            musicvideo 	To define it as music video
            movie 	    To define it as normal movie
            tvshow 	    If this is it defined as tvshow
            season 	    The type is used as a series season
            episode 	The type is used as a series episode
        """
        return str()

    def getOriginalTitle(self):
        """
        To get the original title of the video.

        :return: [string] Original title
        :rtype: str
        """
        return str()

    def getPath(self):
        """
        To get the path where the video is stored.

        :return: [string] Path
        :rtype: str
        """
        return str()

    def getPictureURL(self):
        """
        Get a picture URL of the video to show as screenshot.

        :return: [string] Picture URL
        :rtype: str
        """
        return str()

    def getPlayCount(self):
        """
        To get the number of plays of the video.

        :return: [integer] Play Count
        :rtype: int
        """
        return int()

    def getPlot(self):
        """
        Get the plot of the video if present.

        :return: [string] Plot
        :rtype: str
        """
        return str()

    def getPlotOutline(self):
        """
        Get the outline plot of the video if present.

        :return: [string] Outline plot
        :rtype: str
        """
        return str()

    def getPremiered(self):
        """
        To get premiered date of the video, if available.

        :return: [string]
        :rtype: str
        """
        return str()

    def getRating(self):
        """
        Get the video rating if present as float (double where supported).

        :return: [float] The rating of the video
        :rtype: float
        """
        return float()

    def getSeason(self):
        """
        To get season number of a series

        :return: [integer] season number
        :rtype: int
        """
        return int()

    def getTagLine(self):
        """
        Get video tag line if available.

        :return: [string] Video tag line
        :rtype: str
        """
        return str()

    def getTitle(self):
        """
        Get the video title.

        :return: [string] Video title
        :rtype: str
        """
        return str()

    def getTrailer(self):
        """
        To get the path where the trailer is stored.

        :return: [string] Trailer path
        :rtype: str
        """
        return str()

    def getTVShowTitle(self):
        """
        Get the video TV show title.

        :return: [string] TV show title
        :rtype: str
        """
        return str()

    def getUserRating(self):
        """
        Get the user rating if present as integer.

        :return: [integer] The user rating of the video
        :rtype: int
        """
        return int()

    def getVotes(self):
        """
        Get the video votes if available from video info tag.

        :return: [string] Votes
        :rtype: str
        """
        return str()

    def getWritingCredits(self):
        """
        Get the writing credits if present from video info tag.

        :return: [string] Writing credits
        :rtype: str
        """
        return str()

    def getYear(self):
        """
        Get production year of video if present.

        :return: [integer] Production Year
        :rtype: int
        """
        return int()


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class InfoTagRadioRDS(object):
    """
    To get radio RDS info tag data of currently played PVR radio channel source.

    .. note: Info tag load is only be possible from present player class.
             Also is all the data variable from radio channels and not known on beginning of radio receiving.

    example::

        tag = xbmc.Player().getRadioRDSInfoTag()
        title  = tag.getTitle()
        artist = tag.getArtist()
    """

    def getAlbum(self):
        """
        Album of item on air.

        :return: Album name.
        :rtype: str
        """
        return str()

    def getAlbumTrackNumber(self):
        """
        Get the album track number of currently sended music.

        :return: Track Number.
        :rtype: int
        """
        return int()

    def getArtist(self):
        """
        Artist of the item on air.

        :return: Artist
        :rtype: str
        """
        return str()

    def getBand(self):
        """
        Band of the item on air.

        :return: Band
        :rtype: str
        """
        return str()

    def getComment(self):
        """
        Get Comment text from channel.

        :return: Comment
        :rtype: str
        """
        return str()

    def getComposer(self):
        """
        Get the Composer of the music.

        :return: Composer
        :rtype: str
        """
        return str()

    def getConductor(self):
        """
        Get the Conductor of the Band.

        :return: Conductor
        :rtype: str
        """
        return str()

    def getEditorialStaff(self):
        """
        Get Editorial Staff names.

        :return: Editorial Staff
        :rtype: str
        """
        return str()

    def getEMailHotline(self):
        """
        Email address of the radio station's studio.

        :return: EMail Hotline
        :rtype: str
        """
        return str()

    def getEMailStudio(self):
        """
        Email address of radio station studio.

        :return: EMail Studio.
        :rtype: str
        """
        return str()

    def getInfoCinema(self):
        """
        Get Cinema informations.

        :return: Cinema Information
        :rtype: str
        """
        return str()

    def getInfoHoroscope(self):
        """
        Get Horoscope informations.

        :return: Horoscope Information
        :rtype: str
        """
        return str()

    def getInfoLottery(self):
        """
        Get Lottery informations.

        :return: Lottery Information
        :rtype: str
        """
        return str()

    def getInfoNews(self):
        """
        Get News informations.

        :return: News Information
        :rtype: str
        """
        return str()

    def getInfoNewsLocal(self):
        """
        Get Local news information.

        :return:Local News Information
        :rtype: str
        """
        return str()

    def getInfoOther(self):
        """
        Get other informations.

        :return: Other Information
        :rtype: str
        """
        return str()

    def getInfoSport(self):
        """
        Get Sport information.

        :return: Sport Information
        :rtype: str
        """
        return str()

    def getInfoStock(self):
        """
        Get Stock information.

        :return: Stock Information
        :rtype: str
        """
        return str()

    def getInfoWeather(self):
        """
        Get Weather information.

        :return: Weather Information
        :rtype: str
        """
        return str()

    def getPhoneHotline(self):
        """
        Telephone number of the radio station's hotline.

        :return: Phone Hotline
        :rtype: str
        """
        return str()

    def getPhoneStudio(self):
        """
        Telephone number of the radio station's studio.

        :return: Phone Studio
        :rtype: str
        """
        return str()

    def getProgHost(self):
        """
        Host of current radio show.

        :return: Program Host
        :rtype: str
        """
        return str()

    def getProgNext(self):
        """
        Next program show.

        :return: Program Next
        :rtype: str
        """
        return str()

    def getProgNow(self):
        """
        Current radio program show.

        :return: Program Now
        :rtype: str
        """
        return str()

    def getProgStation(self):
        """
        Name describing station.

        :return: Program Station
        :rtype: str
        """
        return str()

    def getProgStyle(self):
        """
        The the radio channel style currently used.

        :return: Program Style
        :rtype: str
        """
        return str()

    def getProgWebsite(self):
        """
        Link to URL (web page) for radio station homepage.

        :return: Program Website
        :rtype: str
        """
        return str()

    def getSMSStudio(self):
        """
        SMS (Text Messaging) number for studio.

        :return: SMS Studio
        :rtype: str
        """
        return str()

    def getTitle(self):
        """
        Title of the item on the air; i.e. song title.

        :return: Title
        :rtype: str
        """
        return str()


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class Monitor(object):
    """
    Monitor class.

    Creates a new Monitor to notify addon about changes.
    """

    def abortRequested(self):
        """
        Returns ``True`` if abort has been requested.
        :rtype: bool
        """
        return bool(0)

    def onAbortRequested(self):
        """
        .. warning:: Deprecated! Use Function: waitForAbort() to be notified about this event.
        """
        pass

    def onCleanFinished(self, library):
        """
        onCleanFinished method.

        :param str library: video/music as string

        .. note: Will be called when library clean has ended
                 and return video or music to indicate which library has been cleaned
        """
        pass

    def onCleanStarted(self, library):
        """
        onCleanStarted method.

        :param str library: video/music as string

        .. note: Will be called when library clean has started
                 and return video or music to indicate which library is being cleaned
        """
        pass

    def onDatabaseScanStarted(self, database):
        """
        .. warning:: Deprecated! Use Function: onScanStarted().
        """
        pass

    def onDatabaseUpdated(self, database):
        """
        .. warning:: Deprecated! Use Function: onScanFinished().
        """
        pass

    def onDPMSActivated(self):
        """
        onDPMSActivated method.

        .. note: Will be called when energysaving/DPMS gets active
        """
        pass

    def onDPMSDeactivated(self):
        """
        onDPMSDeactivated method.

        .. note: Will be called when energysaving/DPMS is turned off
        """
        pass

    def onNotification(self, sender, method, data):
        """
        onNotification method.

        :param str sender: str - sender of the notification
        :param str method: str - name of the notification
        :param str data: str - JSON-encoded data of the notification

        .. note: Will be called when Kodi receives or sends a notification
        """
        pass

    def onScanFinished(self, library):
        """
        onScanFinished method.

        :param str library: video/music as string

        .. note: Will be called when library scan has ended
                 and return video or music to indicate which library has been scanned
        """
        pass

    def onScanStarted(self, library):
        """
        onScanStarted method.

        :param str library: video/music as string

        .. note: Will be called when library scan has started
                 and return video or music to indicate which library is being scanned
        """
        pass

    def onScreensaverActivated(self):
        """
        onScreensaverActivated method.

        .. note: Will be called when screensaver kicks in
        """
        pass

    def onScreensaverDeactivated(self):
        """
        onScreensaverDeactivated method.

        .. note: Will be called when screensaver goes off
        """
        pass

    def onSettingsChanged(self):
        """
        onSettingsChanged method.

        .. note: Will be called when addon settings are changed
        """
        pass

    def waitForAbort(self, timeout=-1):
        """
        Block until abort is requested, or until timeout occurs.

        If an abort requested have already been made, return immediately.

        :param float timeout: float - [opt] timeout in seconds. Default: no timeout.
        :return: True when abort have been requested, False if a timeout is given and the
        :rtype: bool
        """
        return bool(0)


# noinspection PyMethodMayBeStatic, PyUnusedLocal
class RenderCapture(object):
    """Kodi's render capture."""

    def capture(self, width, height):
        """
        Issue capture request.

        :param int width: Width capture image should be rendered to
        :param int height: Height capture image should should be rendered to
        """
        pass

    def getAspectRatio(self):
        """
        Get aspect ratio of currently displayed video.

        :return: aspect ratio of currently displayed video as a float number.
        :rtype: float
        """
        return float()

    def getHeight(self):
        """
        Get height

        To get height of captured image as set during Function:
        RenderCapture.capture(). Returns 0 prior to calling capture.

        :return: height or 0 prior to calling capture
        :rtype: int
        """
        return int()

    def getImage(self, msecs=0):
        """
        Returns captured image as a bytearray.

        :param msecs: [opt] wait time in msec
        :return: captured image as a bytearray.
        :rtype: bytearray

        .. note: The size of the image isgetWidth() * getHeight() * 4
        """
        return bytearray()

    def getImageFormat(self):
        """
        Get image format

        :return: format of captured image: 'BGRA' or 'RGBA'.
        :rtype: str
        """
        return str()

    def getWidth(self):
        """
        Get width

        To get width of captured image as set during Function:
        RenderCapture.capture(). Returns 0 prior to calling capture.

        :return: Width or 0 prior to calling capture.
        :rtype: int
        """
        return int()
