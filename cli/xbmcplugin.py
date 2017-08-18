"""
Offers classes and functions that allow a developer to present information through Kodi's standard menu
structure. While plugins don't have the same flexibility as scripts, they boast significantly quicker
development time and a more consistent user experience.
"""

# Package imports
from codequickcli.support import plugin_data

__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:19 BST 2015'
__platform__ = 'ALL'
__version__ = '2.25.0'

SORT_METHOD_VIDEO_USER_RATING = 20
SORT_METHOD_SONG_USER_RATING = 30
SORT_METHOD_ALBUM = 14
SORT_METHOD_ALBUM_IGNORE_THE = 15
SORT_METHOD_ARTIST = 11
SORT_METHOD_ARTIST_IGNORE_THE = 13
SORT_METHOD_BITRATE = 43
SORT_METHOD_CHANNEL = 41
SORT_METHOD_COUNTRY = 17
SORT_METHOD_DATE = 3
SORT_METHOD_DATEADDED = 21
SORT_METHOD_DATE_TAKEN = 44
SORT_METHOD_DRIVE_TYPE = 6
SORT_METHOD_DURATION = 8
SORT_METHOD_EPISODE = 24
SORT_METHOD_FILE = 5
SORT_METHOD_FULLPATH = 35
SORT_METHOD_GENRE = 16
SORT_METHOD_LABEL = 1
SORT_METHOD_LABEL_IGNORE_FOLDERS = 36
SORT_METHOD_LABEL_IGNORE_THE = 2
SORT_METHOD_LASTPLAYED = 37
SORT_METHOD_LISTENERS = 39
SORT_METHOD_MPAA_RATING = 31
SORT_METHOD_NONE = 0
SORT_METHOD_PLAYCOUNT = 38
SORT_METHOD_PLAYLIST_ORDER = 23
SORT_METHOD_PRODUCTIONCODE = 28
SORT_METHOD_PROGRAM_COUNT = 22
SORT_METHOD_SIZE = 4
SORT_METHOD_SONG_RATING = 29
SORT_METHOD_STUDIO = 33
SORT_METHOD_STUDIO_IGNORE_THE = 34
SORT_METHOD_TITLE = 9
SORT_METHOD_TITLE_IGNORE_THE = 10
SORT_METHOD_TRACKNUM = 7
SORT_METHOD_UNSORTED = 40
SORT_METHOD_VIDEO_RATING = 19
SORT_METHOD_VIDEO_RUNTIME = 32
SORT_METHOD_VIDEO_SORT_TITLE = 26
SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE = 27
SORT_METHOD_VIDEO_TITLE = 25
SORT_METHOD_VIDEO_YEAR = 18


# noinspection PyUnusedLocal, PyTypeChecker
def addDirectoryItem(handle, url, listitem, isFolder=False, totalItems=0):
    """
    Callback function to pass directory contents back to XBMC.

    Returns a bool for successful completion.

    :param int handle: integer - handle the plugin was started with.
    :param str url: string - url of the entry. would be plugin:// for another virtual directory.
    :param listitem: ListItem - item to add.
    :param bool isFolder: [opt] bool - True=folder / False=not a folder.
    :param int totalItems: [opt] integer - total number of items that will be passed. (used for progressbar)

    :returns: Returns a bool for successful completion.
    :rtype: bool

    Example::

        if not xbmcplugin.addDirectoryItem(int(sys.argv[1]), 'F:\\Trailers\\300.mov', listitem, totalItems=50):
            break
    """
    data = (url, listitem, isFolder)
    plugin_data["listitem"].append(data)
    return True


# noinspection PyUnusedLocal
def addDirectoryItems(handle, items, totalItems=0):
    """
    Callback function to pass directory contents back to XBMC as a list.

    Returns a bool for successful completion.

    :param int handle: integer - handle the plugin was started with.
    :param list items: List - list of (url, listitem[, isFolder]) as a tuple to add.
    :param int totalItems: [opt] integer - total number of items that will be passed. (used for progressbar)

    :returns: Returns a bool for successful completion.
    :rtype: bool

    .. note::
        Large lists benefit over using the standard addDirectoryItem().
        You may call this more than once to add items in chunks.

    .. note:: Large lists benefit over using the standard Function: addDirectoryItem().
              You may call this more than once to add items in chunks

    Example::

        if not xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(url, listitem, False,)]:
            raise
    """
    plugin_data["listitem"].extend(items)
    return True


# noinspection PyUnusedLocal
def addSortMethod(handle, sortMethod, label2Mask=""):
    """
    Adds a sorting method for the media list.

    :param int handle: integer - handle the plugin was started with.
    :param int sortMethod: integer - number for sortmethod see FileItem.h.
    :param str label2Mask: [opt] string - the label mask to use for the second label. Defaults to '%D'

    sortMethod Options::

        xbmcplugin.SORT_METHOD_NONE         	    Do not sort
        xbmcplugin.SORT_METHOD_LABEL 	            Sort by label
        xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE     Sort by the label and ignore "The" before
        xbmcplugin.SORT_METHOD_DATE 	            Sort by the date
        xbmcplugin.SORT_METHOD_SIZE 	            Sort by the size
        xbmcplugin.SORT_METHOD_FILE 	            Sort by the file
        xbmcplugin.SORT_METHOD_DRIVE_TYPE 	        Sort by the drive type
        xbmcplugin.SORT_METHOD_TRACKNUM 	        Sort by the track number
        xbmcplugin.SORT_METHOD_DURATION 	        Sort by the duration
        xbmcplugin.SORT_METHOD_TITLE 	            Sort by the title
        xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE     Sort by the title and ignore "The" before
        xbmcplugin.SORT_METHOD_ARTIST 	            Sort by the artist
        xbmcplugin.SORT_METHOD_ARTIST_IGNORE_THE 	Sort by the artist and ignore "The" before
        xbmcplugin.SORT_METHOD_ALBUM 	            Sort by the album
        xbmcplugin.SORT_METHOD_ALBUM_IGNORE_THE 	Sort by the album and ignore "The" before
        xbmcplugin.SORT_METHOD_GENRE 	            Sort by the genre
        xbmcplugin.SORT_SORT_METHOD_VIDEO_YEAR      Sort by the year
        xbmcplugin.SORT_METHOD_YEAR 	            Sort by the year
        xbmcplugin.SORT_METHOD_VIDEO_RATING 	    Sort by the video rating
        xbmcplugin.SORT_METHOD_PROGRAM_COUNT 	    Sort by the program count
        xbmcplugin.SORT_METHOD_PLAYLIST_ORDER 	    Sort by the playlist order
        xbmcplugin.SORT_METHOD_EPISODE 	            Sort by the episode
        xbmcplugin.SORT_METHOD_VIDEO_TITLE 	        Sort by the video title
        xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE 	Sort by the video sort title
        xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE 	Sort by the video sort title and ignore "The" before
        xbmcplugin.SORT_METHOD_PRODUCTIONCODE 	    Sort by the production code
        xbmcplugin.SORT_METHOD_SONG_RATING 	        Sort by the song rating
        xbmcplugin.SORT_METHOD_MPAA_RATING 	        Sort by the mpaa rating
        xbmcplugin.SORT_METHOD_VIDEO_RUNTIME 	    Sort by video runtime
        xbmcplugin.SORT_METHOD_STUDIO 	            Sort by the studio
        xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE 	Sort by the studio and ignore "The" before
        xbmcplugin.SORT_METHOD_UNSORTED 	        Use list not sorted
        xbmcplugin.SORT_METHOD_BITRATE 	            Sort by the bitrate
        xbmcplugin.SORT_METHOD_LISTENERS 	        Sort by the listeners
        xbmcplugin.SORT_METHOD_COUNTRY 	            Sort by the country
        xbmcplugin.SORT_METHOD_DATEADDED 	        Sort by the added date
        xbmcplugin.SORT_METHOD_FULLPATH 	        Sort by the full path name
        xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS Sort by the label names and ignore related folder names
        xbmcplugin.SORT_METHOD_LASTPLAYED 	        Sort by last played date
        xbmcplugin.SORT_METHOD_PLAYCOUNT 	        Sort by the play count
        xbmcplugin.SORT_METHOD_CHANNEL 	            Sort by the channel
        xbmcplugin.SORT_METHOD_DATE_TAKEN 	        Sort by the taken date
        xbmcplugin.SORT_METHOD_VIDEO_USER_RATING 	Sort by the rating of the user of video
        xbmcplugin.SORT_METHOD_SONG_USER_RATING 	Sort by the rating of the user of song

    label2Mask applies to::

        SORT_METHOD_NONE, SORT_METHOD_UNSORTED, SORT_METHOD_VIDEO_TITLE, SORT_METHOD_TRACKNUM,
        SORT_METHOD_FILE, SORT_METHOD_TITLE, SORT_METHOD_TITLE_IGNORE_THE, SORT_METHOD_LABEL,
        SORT_METHOD_LABEL_IGNORE_THE, SORT_METHOD_VIDEO_SORT_TITLE, SORT_METHOD_FULLPATH,
        SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE, SORT_METHOD_LABEL_IGNORE_FOLDERS, SORT_METHOD_CHANNEL

    .. note:: to add multiple sort methods just call the method multiple times.

    Example::

        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    """
    plugin_data["sortmethods"].append(sortMethod)


# noinspection PyUnusedLocal
def endOfDirectory(handle, succeeded=True, updateListing=False, cacheToDisc=True):
    """
    Callback function to tell XBMC that the end of the directory listing in a virtualPythonFolder module is reached.

    :param int handle: integer - handle the plugin was started with.
    :param bool succeeded: [opt] bool - True=script completed successfully(Default)/False=Script did not.
    :param bool updateListing: [opt] bool - True=this folder should add the current listing/
                                            False=Folder is a subfolder.(Default)
    :param bool cacheToDisc: [opt] bool - True=Folder will cache if extended time(Default)/
                                          False=will never cache to disc.

    Example::

        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
    """
    plugin_data["succeeded"] = succeeded
    plugin_data["updatelisting"] = updateListing


# noinspection PyUnusedLocal
def getSetting(handle, id):
    """
    Returns the value of a setting as a string.

    :param int handle: integer - handle the plugin was started with.
    :param str id: string - id of the setting that the module needs to access.

    :returns: Setting value as string
    :rtype: str

    Example::

        apikey = xbmcplugin.getSetting(int(sys.argv[1]), 'apikey')
    """
    return str()


# noinspection PyUnusedLocal
def setContent(handle, content):
    """
    Sets the plugins content type.

    :param int handle: integer - handle the plugin was started with.
    :param str content: string - content type (eg. movies).

    Possible values for content::

        Possible values for content: files, songs, artists, albums, movies, tvshows,
                                     episodes, musicvideos, videos, games

    Example::

        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    """
    plugin_data["contenttype"] = content


# noinspection PyUnusedLocal
def setPluginCategory(handle, category):
    """
    Sets the plugins name for skins to display.

    :param int handle: integer - handle the plugin was started with.
    :param category: string or unicode - plugins sub category.
    :type category: str or unicode

    Example::

        xbmcplugin.setPluginCategory(int(sys.argv[1]), 'Comedy')
    """
    plugin_data["category"] = category


# noinspection PyUnusedLocal
def setPluginFanart(handle, image=None, color1=None, color2=None, color3=None):
    """
    Sets the plugins fanart and color for skins to display.

    :param int handle: integer - handle the plugin was started with.
    :param str image: [opt] string - kodi_path to fanart image.
    :param str color1: [opt] hexstring - color1. (e.g. '0xFFFFFFFF')
    :param str color2: [opt] hexstring - color2. (e.g. '0xFFFF3300')
    :param str color3: [opt] hexstring - color3. (e.g. '0xFF000000')

    Example::

        xbmcplugin.setPluginFanart(int(sys.argv[1]),
        special://home/addons/plugins/video/Apple movie trailers II/fanart.png', color2='0xFFFF3300')
    """
    pass


# noinspection PyUnusedLocal
def setProperty(handle, key, value):
    """
    Sets a container property for this plugin.

    :param int handle: integer - handle the plugin was started with.
    :param str key: string - property name.
    :param value: string or unicode - value of property.
    :type value: str or unicode

    .. note::
        Key is NOT case sensitive.

    Example::

        xbmcplugin.setProperty(int(sys.argv[1]), 'Emulator', 'M.A.M.E.')
    """
    pass


# noinspection PyUnusedLocal
def setResolvedUrl(handle, succeeded, listitem):
    """
    Callback function to tell Kodi that the file plugin has been resolved to a url

    :param int handle: integer - handle the plugin was started with.
    :param bool succeeded: bool - True=script completed successfully/False=Script did not.
    :param listitem: ListItem - item the file plugin resolved to for playback.

    Example::

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
    """
    plugin_data["resolved"] = listitem
    plugin_data["succeeded"] = succeeded


# noinspection PyUnusedLocal
def setSetting(handle, id, value):
    """
    Sets a plugin setting for the current running plugin.

    :param int handle: integer - handle the plugin was started with.
    :param str id: string - id of the setting that the module needs to access.
    :param value: string or unicode - value of the setting.
    :type value: str or unicode

    Example::

        xbmcplugin.set_setting(int(sys.argv[1]), id='username', value='teamxbmc')
    """
    pass
