"""
Offers classes and functions that manipulate the Graphical User Interface through windows,
dialogs, and various control widgets.
"""
# Standard Library Imports
from __future__ import print_function
import warnings

# Package imports
import codequickcli.support as _support

__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:15 BST 2015'
__platform__ = 'ALL'
__version__ = '2.25.0'

ACTION_ANALOG_FORWARD = 113
ACTION_ANALOG_MOVE = 49
ACTION_ANALOG_MOVE_X = 601
ACTION_ANALOG_MOVE_Y = 602
ACTION_ANALOG_REWIND = 114
ACTION_ANALOG_SEEK_BACK = 125
ACTION_ANALOG_SEEK_FORWARD = 124
ACTION_ASPECT_RATIO = 19
ACTION_AUDIO_DELAY = 161
ACTION_AUDIO_DELAY_MIN = 54
ACTION_AUDIO_DELAY_PLUS = 55
ACTION_AUDIO_NEXT_LANGUAGE = 56
ACTION_BACKSPACE = 110
ACTION_BIG_STEP_BACK = 23
ACTION_BIG_STEP_FORWARD = 22
ACTION_BUILT_IN_FUNCTION = 122
ACTION_CALIBRATE_RESET = 48
ACTION_CALIBRATE_SWAP_ARROWS = 47
ACTION_CHANGE_RESOLUTION = 57
ACTION_CHANNEL_DOWN = 185
ACTION_CHANNEL_SWITCH = 183
ACTION_CHANNEL_UP = 184
ACTION_CHAPTER_OR_BIG_STEP_BACK = 98
ACTION_CHAPTER_OR_BIG_STEP_FORWARD = 97
ACTION_CONTEXT_MENU = 117
ACTION_COPY_ITEM = 81
ACTION_CREATE_BOOKMARK = 96
ACTION_CREATE_EPISODE_BOOKMARK = 95
ACTION_CURSOR_LEFT = 120
ACTION_CURSOR_RIGHT = 121
ACTION_CYCLE_SUBTITLE = 99
ACTION_DECREASE_PAR = 220
ACTION_DECREASE_RATING = 137
ACTION_DELETE_ITEM = 80
ACTION_ENTER = 135
ACTION_ERROR = 998
ACTION_FILTER = 233
ACTION_FILTER_CLEAR = 150
ACTION_FILTER_SMS2 = 151
ACTION_FILTER_SMS3 = 152
ACTION_FILTER_SMS4 = 153
ACTION_FILTER_SMS5 = 154
ACTION_FILTER_SMS6 = 155
ACTION_FILTER_SMS7 = 156
ACTION_FILTER_SMS8 = 157
ACTION_FILTER_SMS9 = 158
ACTION_FIRST_PAGE = 159
ACTION_FORWARD = 16
ACTION_GESTURE_BEGIN = 501
ACTION_GESTURE_END = 599
ACTION_GESTURE_NOTIFY = 500
ACTION_GESTURE_PAN = 504
ACTION_GESTURE_ROTATE = 503
ACTION_GESTURE_SWIPE_DOWN = 541
ACTION_GESTURE_SWIPE_DOWN_TEN = 550
ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_GESTURE_SWIPE_LEFT_TEN = 520
ACTION_GESTURE_SWIPE_RIGHT = 521
ACTION_GESTURE_SWIPE_RIGHT_TEN = 530
ACTION_GESTURE_SWIPE_UP = 531
ACTION_GESTURE_SWIPE_UP_TEN = 540
ACTION_GESTURE_ZOOM = 502
ACTION_GUIPROFILE_BEGIN = 204
ACTION_HIGHLIGHT_ITEM = 8
ACTION_INCREASE_PAR = 219
ACTION_INCREASE_RATING = 136
ACTION_INPUT_TEXT = 244
ACTION_JUMP_SMS2 = 142
ACTION_JUMP_SMS3 = 143
ACTION_JUMP_SMS4 = 144
ACTION_JUMP_SMS5 = 145
ACTION_JUMP_SMS6 = 146
ACTION_JUMP_SMS7 = 147
ACTION_JUMP_SMS8 = 148
ACTION_JUMP_SMS9 = 149
ACTION_LAST_PAGE = 160
ACTION_MOUSE_DOUBLE_CLICK = 103
ACTION_MOUSE_DRAG = 106
ACTION_MOUSE_END = 109
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_LONG_CLICK = 108
ACTION_MOUSE_MIDDLE_CLICK = 102
ACTION_MOUSE_MOVE = 107
ACTION_MOUSE_RIGHT_CLICK = 101
ACTION_MOUSE_START = 100
ACTION_MOUSE_WHEEL_DOWN = 105
ACTION_MOUSE_WHEEL_UP = 104
ACTION_MOVE_DOWN = 4
ACTION_MOVE_ITEM = 82
ACTION_MOVE_ITEM_DOWN = 116
ACTION_MOVE_ITEM_UP = 115
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MUTE = 91
ACTION_NAV_BACK = 92
ACTION_NEXT_CHANNELGROUP = 186
ACTION_NEXT_CONTROL = 181
ACTION_NEXT_ITEM = 14
ACTION_NEXT_LETTER = 140
ACTION_NEXT_PICTURE = 28
ACTION_NEXT_SCENE = 138
ACTION_NEXT_SUBTITLE = 26
ACTION_NONE = 0
ACTION_NOOP = 999
ACTION_OSD_HIDESUBMENU = 84
ACTION_OSD_SHOW_DOWN = 72
ACTION_OSD_SHOW_LEFT = 69
ACTION_OSD_SHOW_RIGHT = 70
ACTION_OSD_SHOW_SELECT = 73
ACTION_OSD_SHOW_UP = 71
ACTION_OSD_SHOW_VALUE_MIN = 75
ACTION_OSD_SHOW_VALUE_PLUS = 74
ACTION_PAGE_DOWN = 6
ACTION_PAGE_UP = 5
ACTION_PARENT_DIR = 9
ACTION_PASTE = 180
ACTION_PAUSE = 12
ACTION_PLAY = 68
ACTION_PLAYER_FORWARD = 77
ACTION_PLAYER_PLAY = 79
ACTION_PLAYER_PLAYPAUSE = 229
ACTION_PLAYER_REWIND = 78
ACTION_PREVIOUS_CHANNELGROUP = 187
ACTION_PREVIOUS_MENU = 10
ACTION_PREV_CONTROL = 182
ACTION_PREV_ITEM = 15
ACTION_PREV_LETTER = 141
ACTION_PREV_PICTURE = 29
ACTION_PREV_SCENE = 139
ACTION_PVR_PLAY = 188
ACTION_PVR_PLAY_RADIO = 190
ACTION_PVR_PLAY_TV = 189
ACTION_QUEUE_ITEM = 34
ACTION_RECORD = 170
ACTION_RELOAD_KEYMAPS = 203
ACTION_REMOVE_ITEM = 35
ACTION_RENAME_ITEM = 87
ACTION_REWIND = 17
ACTION_ROTATE_PICTURE_CCW = 51
ACTION_ROTATE_PICTURE_CW = 50
ACTION_SCAN_ITEM = 201
ACTION_SCROLL_DOWN = 112
ACTION_SCROLL_UP = 111
ACTION_SELECT_ITEM = 7
ACTION_SETTINGS_LEVEL_CHANGE = 242
ACTION_SETTINGS_RESET = 241
ACTION_SHIFT = 118
ACTION_SHOW_CODEC = 27
ACTION_SHOW_FULLSCREEN = 36
ACTION_SHOW_GUI = 18
ACTION_SHOW_INFO = 11
ACTION_SHOW_MPLAYER_OSD = 83
ACTION_SHOW_OSD = 24
ACTION_SHOW_OSD_TIME = 123
ACTION_SHOW_PLAYLIST = 33
ACTION_SHOW_SUBTITLES = 25
ACTION_SHOW_VIDEOMENU = 134
ACTION_SMALL_STEP_BACK = 76
ACTION_STEP_BACK = 21
ACTION_STEP_FORWARD = 20
ACTION_STEREOMODE_NEXT = 235
ACTION_STEREOMODE_PREVIOUS = 236
ACTION_STEREOMODE_SELECT = 238
ACTION_STEREOMODE_SET = 240
ACTION_STEREOMODE_TOGGLE = 237
ACTION_STEREOMODE_TOMONO = 239
ACTION_STOP = 13
ACTION_SUBTITLE_ALIGN = 232
ACTION_SUBTITLE_DELAY = 162
ACTION_SUBTITLE_DELAY_MIN = 52
ACTION_SUBTITLE_DELAY_PLUS = 53
ACTION_SUBTITLE_VSHIFT_DOWN = 231
ACTION_SUBTITLE_VSHIFT_UP = 230
ACTION_SWITCH_PLAYER = 234
ACTION_SYMBOLS = 119
ACTION_TAKE_SCREENSHOT = 85
ACTION_TELETEXT_BLUE = 218
ACTION_TELETEXT_GREEN = 216
ACTION_TELETEXT_RED = 215
ACTION_TELETEXT_YELLOW = 217
ACTION_TOGGLE_DIGITAL_ANALOG = 202
ACTION_TOGGLE_FULLSCREEN = 199
ACTION_TOGGLE_SOURCE_DEST = 32
ACTION_TOGGLE_WATCHED = 200
ACTION_TOUCH_LONGPRESS = 411
ACTION_TOUCH_LONGPRESS_TEN = 420
ACTION_TOUCH_TAP = 401
ACTION_TOUCH_TAP_TEN = 410
ACTION_TRIGGER_OSD = 243
ACTION_VIS_PRESET_LOCK = 130
ACTION_VIS_PRESET_NEXT = 128
ACTION_VIS_PRESET_PREV = 129
ACTION_VIS_PRESET_RANDOM = 131
ACTION_VIS_PRESET_SHOW = 126
ACTION_VIS_RATE_PRESET_MINUS = 133
ACTION_VIS_RATE_PRESET_PLUS = 132
ACTION_VOLAMP = 90
ACTION_VOLAMP_DOWN = 94
ACTION_VOLAMP_UP = 93
ACTION_VOLUME_DOWN = 89
ACTION_VOLUME_SET = 245
ACTION_VOLUME_UP = 88
ACTION_VSHIFT_DOWN = 228
ACTION_VSHIFT_UP = 227
ACTION_ZOOM_IN = 31
ACTION_ZOOM_LEVEL_1 = 38
ACTION_ZOOM_LEVEL_2 = 39
ACTION_ZOOM_LEVEL_3 = 40
ACTION_ZOOM_LEVEL_4 = 41
ACTION_ZOOM_LEVEL_5 = 42
ACTION_ZOOM_LEVEL_6 = 43
ACTION_ZOOM_LEVEL_7 = 44
ACTION_ZOOM_LEVEL_8 = 45
ACTION_ZOOM_LEVEL_9 = 46
ACTION_ZOOM_LEVEL_NORMAL = 37
ACTION_ZOOM_OUT = 30
ALPHANUM_HIDE_INPUT = 2
CONTROL_TEXT_OFFSET_X = 10
CONTROL_TEXT_OFFSET_Y = 2
ICON_OVERLAY_HD = 6
ICON_OVERLAY_LOCKED = 3
ICON_OVERLAY_NONE = 0
ICON_OVERLAY_RAR = 1
ICON_OVERLAY_UNWATCHED = 4
ICON_OVERLAY_WATCHED = 5
ICON_OVERLAY_ZIP = 2
ICON_TYPE_FILES = 106
ICON_TYPE_MUSIC = 103
ICON_TYPE_NONE = 101
ICON_TYPE_PICTURES = 104
ICON_TYPE_PROGRAMS = 102
ICON_TYPE_SETTINGS = 109
ICON_TYPE_VIDEOS = 105
ICON_TYPE_WEATHER = 107
INPUT_ALPHANUM = 0
INPUT_DATE = 2
INPUT_IPADDRESS = 4
INPUT_NUMERIC = 1
INPUT_PASSWORD = 5
INPUT_TIME = 3
KEY_APPCOMMAND = 53248
KEY_ASCII = 61696
KEY_BUTTON_A = 256
KEY_BUTTON_B = 257
KEY_BUTTON_BACK = 275
KEY_BUTTON_BLACK = 260
KEY_BUTTON_DPAD_DOWN = 271
KEY_BUTTON_DPAD_LEFT = 272
KEY_BUTTON_DPAD_RIGHT = 273
KEY_BUTTON_DPAD_UP = 270
KEY_BUTTON_LEFT_ANALOG_TRIGGER = 278
KEY_BUTTON_LEFT_THUMB_BUTTON = 276
KEY_BUTTON_LEFT_THUMB_STICK = 264
KEY_BUTTON_LEFT_THUMB_STICK_DOWN = 281
KEY_BUTTON_LEFT_THUMB_STICK_LEFT = 282
KEY_BUTTON_LEFT_THUMB_STICK_RIGHT = 283
KEY_BUTTON_LEFT_THUMB_STICK_UP = 280
KEY_BUTTON_LEFT_TRIGGER = 262
KEY_BUTTON_RIGHT_ANALOG_TRIGGER = 279
KEY_BUTTON_RIGHT_THUMB_BUTTON = 277
KEY_BUTTON_RIGHT_THUMB_STICK = 265
KEY_BUTTON_RIGHT_THUMB_STICK_DOWN = 267
KEY_BUTTON_RIGHT_THUMB_STICK_LEFT = 268
KEY_BUTTON_RIGHT_THUMB_STICK_RIGHT = 269
KEY_BUTTON_RIGHT_THUMB_STICK_UP = 266
KEY_BUTTON_RIGHT_TRIGGER = 263
KEY_BUTTON_START = 274
KEY_BUTTON_WHITE = 261
KEY_BUTTON_X = 258
KEY_BUTTON_Y = 259
KEY_INVALID = 65535
KEY_MOUSE_CLICK = 57344
KEY_MOUSE_DOUBLE_CLICK = 57360
KEY_MOUSE_DRAG = 57604
KEY_MOUSE_DRAG_END = 57606
KEY_MOUSE_DRAG_START = 57605
KEY_MOUSE_END = 61439
KEY_MOUSE_LONG_CLICK = 57376
KEY_MOUSE_MIDDLECLICK = 57346
KEY_MOUSE_MOVE = 57603
KEY_MOUSE_NOOP = 61439
KEY_MOUSE_RDRAG = 57607
KEY_MOUSE_RDRAG_END = 57609
KEY_MOUSE_RDRAG_START = 57608
KEY_MOUSE_RIGHTCLICK = 57345
KEY_MOUSE_START = 57344
KEY_MOUSE_WHEEL_DOWN = 57602
KEY_MOUSE_WHEEL_UP = 57601
KEY_TOUCH = 61440
KEY_UNICODE = 61952
KEY_VKEY = 61440
KEY_VMOUSE = 61439
NOTIFICATION_ERROR = 'error'
NOTIFICATION_INFO = 'info'
NOTIFICATION_WARNING = 'warning'
PASSWORD_VERIFY = 1
REMOTE_0 = 58
REMOTE_1 = 59
REMOTE_2 = 60
REMOTE_3 = 61
REMOTE_4 = 62
REMOTE_5 = 63
REMOTE_6 = 64
REMOTE_7 = 65
REMOTE_8 = 66
REMOTE_9 = 67


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ListItem(dict):
    """
    The list item control is used for creating item lists in Kodi

    :type label: str or unicode
    :param label: string or unicode - label1 text.

    :type label: str or unicode
    :param label2: string or unicode - label2 text.

    :param str iconImage: Deprecated. Use setArt
    :param str thumbnailImage: Deprecated. Use setArt

    :type path: str or unicode
    :param path: string or unicode - listitem's path.

    .. warning:: Starting from 16.0 (Jarvis) all image-related parameters and methods will be depreciated,
        and :func:`setArt` will become the only method for setting ListItem's images.

    Example::

        listitem = xbmcgui.ListItem('Casino Royale', '[PG-13]',
                    'blank-poster.tbn', 'poster.tbn',
                    path='f:\\movies\\casino_royale.mov')
    """

    def __init__(self, label="", label2="", iconImage=None, thumbnailImage=None, path=None):
        super(ListItem, self).__init__()

        if label:
            self.setLabel(label)
        if label2:
            self.setLabel2(label2)
        if path:
            self.setPath(path)

        if iconImage:
            warnings.warn("'ListItem(iconImage=image)' is deprecated, use setArt.", DeprecationWarning)
        if thumbnailImage:
            warnings.warn("'ListItem(thumbnailImage=image)' is deprecated, use setArt.", DeprecationWarning)

    def addStreamInfo(self, cType, dictionary):
        """
        addStreamInfo(type, values) -- Add a stream with details.

        :param str cType: string - type of stream(video/audio/subtitle).
        :param dict dictionary: dictionary - pairs of { label: value }.

        Video Values::

            codec         : string (h264)
            aspect        : float (1.78)
            width         : integer (1280)
            height        : integer (720)
            duration      : integer (seconds)

        Audio Values::

            codec         : string (dts)
            language      : string (en)
            channels      : integer (2)

        Subtitle Values::

            language      : string (en)

        example::

            self.list.getSelectedItem().addStreamInfo('video', { 'Codec': 'h264', 'Width' : 1280 })
        """
        self.setdefault("stream", {})[cType] = dictionary

    def getLabel(self):
        """
        Returns the listitem label.
        :rtype: str
        """
        return _support.ensure_native_str(self.get("label", u""))

    def getLabel2(self):
        """
        Returns the listitem's second label.
        :rtype: str
        """
        return _support.ensure_native_str(self.get("label2", u""))

    def setLabel(self, label):
        """
        Sets the listitem's label.

        :param label: string or unicode - text string.
        :type label: str or unicode
        """
        self["label"] = _support.ensure_unicode(label)

    def setLabel2(self, label2):
        """
        Sets the listitem's second label.

        :param label2: string or unicode - text string.
        :type label2: str or unicode
        """
        self["label2"] = _support.ensure_unicode(label2)

    def setIconImage(self, iconImage):
        """
        Sets the listitem's icon image.

        :param iconImage: string or unicode - image filename.
        :type iconImage: str or unicode
        """
        warnings.warn("method 'Listitem.setIconImage' is deprecated, use setArt.", DeprecationWarning)

    def setThumbnailImage(self, thumbFilename):
        """
        Sets the listitem's thumbnail image.

        :param thumbFilename: string or unicode - image filename.
        :type thumbFilename: str or unicode
        """
        warnings.warn("method 'Listitem.setThumbnailImage' is deprecated, use setArt.", DeprecationWarning)

    def setContentLookup(self, enable):
        """
        Enable or disable content lookup for item.

        If disabled, HEAD requests to e.g determine mime type will not be sent.
        
        :param bool enable: True/False to Enable or disable content lookup.
        """
        self["content_lookup"] = enable

    def setInfo(self, ctype, infoLabels):
        """
        Sets the listitem's infoLabels.

        :param str ctype: string - type of media(video/music/pictures).
        :param dict infoLabels: dictionary - pairs of { label: value }.

        .. note::
            To set pictures exif info, prepend 'exif:' to the label. Exif values must be passed
            as strings, separate value pairs with a comma. (eg. {'exif:resolution': '720,480'}
            See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings.

        General Values that apply to all types:

            * count: integer (12) - can be used to store an id for later, or for sorting purposes
            * size: long (1024) - size in bytes
            * date: string (%d.%m.%Y / 01.01.2009) - file date

        Video Values::

            genre: string (Comedy)
            year: integer (2009)
            episode: integer (4)
            season: integer (1)
            top250: integer (192)
            tracknumber: integer (3)
            rating: float (6.4) - range is 0..10
            watched: depreciated - use playcount instead
            playcount: integer (2) - number of times this item has been played
            overlay: integer (2) - range is 0..8.  See GUIListItem.h for values
            cast: list (Michal C. Hall)
            castandrole: list (Michael C. Hall|Dexter)
            director: string (Dagur Kari)
            mpaa: string (PG-13)
            plot: string (Long Description)
            plotoutline: string (Short Description)
            title: string (Big Fan)
            originaltitle: string (Big Fan)
            duration: string - duration in minutes (95)
            studio: string (Warner Bros.)
            tagline: string (An awesome movie) - short description of movie
            writer: string (Robert D. Siegel)
            tvshowtitle: string (Heroes)
            premiered: string (2005-03-04)
            status: string (Continuing) - status of a TVshow
            code: string (tt0110293) - IMDb code
            aired: string (2008-12-07)
            credits: string (Andy Kaufman) - writing credits
            lastplayed: string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)
            album: string (The Joshua Tree)
            votes: string (12345 votes)
            trailer: string (/home/user/trailer.avi)
            imdbnumber : string (tt0110293) - IMDb code
            set : string (Batman Collection) - name of the collection
            setid : integer (14) - ID of the collection

        Music Values::

            tracknumber: integer (8)
            duration: integer (245) - duration in seconds
            year: integer (1998)
            genre: string (Rock)
            album: string (Pulse)
            artist: string (Muse)
            title: string (American Pie)
            rating: string (3) - single character between 0 and 5
            lyrics: string (On a dark desert highway...)
            playcount: integer (2) - number of times this item has been played
            lastplayed: string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)

        Picture Values::

            title: string (In the last summer-1)
            picturepath: string (/home/username/pictures/img001.jpg)
            exif: string (See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings)

        Example::

            self.list.getSelectedItem().setInfo('video', { 'Genre': 'Comedy' })
        """
        self["info"] = infoLabels

    def setProperty(self, key, value):
        """
        Sets a listitem property, similar to an infolabel.

        :param str key: string - property name.
        :param value: string or unicode - value of property.
        :type value: str or unicode

        .. note::
            Key is NOT case sensitive.

        Some of these are treated internally by XBMC, such as the 'StartOffset' property, which is
        the offset in seconds at which to start playback of an item.  Others may be used in the skin
        to add extra information, such as 'WatchedCount' for tvshow items

        Example::

            self.list.getSelectedItem().setProperty('AspectRatio', '1.85 : 1')
            self.list.getSelectedItem().setProperty('StartOffset', '256.4')
        """
        self.setdefault("properties", {})[key] = _support.ensure_unicode(value)

    def getProperty(self, key):
        """Returns a listitem property as a string, similar to an infolabel.

        :param str key: string - property name.

        .. note::
            Key is NOT case sensitive.
        """
        return _support.ensure_native_str(self.setdefault("properties", {})[key])

    def addContextMenuItems(self, items, replaceItems=False):
        """Adds item(s) to the context menu for media lists.

        :param list items: list - [(label, action)] A list of tuples consisting of label and action pairs.
            label: string or unicode - item's label.
            action: string or unicode - any built-in function to perform.
        :param bool replaceItems: bool - True=only your items will show/False=your items will be added to context menu.

        List of functions: http://wiki.xbmc.org/?title=List_of_Built_In_Functions

        Example::

            listitem.addContextMenuItems([('Theater Showtimes',
                    'XBMC.RunScript(special://home/scripts/showtimes/default.py,Iron Man)')])
        """
        self.setdefault("context", []).extend(items)

    def setPath(self, path):
        """
        Sets the listitem's path.

        :param path: string or unicode - path, activated when item is clicked.
        :type path: str or unicode

        .. note:: You can use the above as keywords for arguments.

        example::

            self.list.getSelectedItem().setPath(path='ActivateWindow(Weather)')
        """
        self["path"] = _support.ensure_unicode(path)

    def setArt(self, dictionary):
        """
        Sets the listitem's art

        :param dict dictionary: dict - pairs of { label: value }.

        Some default art values (any string possible):

        * thumb : string - image filename
        * poster : string - image filename
        * banner : string - image filename
        * fanart : string - image filename
        * clearart : string - image filename
        * clearlogo : string - image filename
        * landscape : string - image filename

        .. warning:: Starting from 16.0 (Jarvis) all image-related parameters and methods will be depreciated,
            and ``setArt`` will become the only method for setting ListItem's images.

        example::

            self.list.getSelectedItem().setArt({ 'poster': 'poster.png', 'banner' : 'banner.png' })
        """
        self.setdefault("art", {}).update(dictionary)

    def setMimeType(self, mimetype):
        """
        Sets the listitem's mimetype if known.

        :param mimetype : string or unicode - mimetype.
        :type mimetype: str or unicode

        If known prehand, this can avoid xbmc doing ``HEAD`` requests to http servers to figure out file type.
        """
        self["mimetype"] = _support.ensure_unicode(mimetype)

    def isSelected(self):
        """
        Returns the listitem's selected status.

        :returns: true if selected, otherwise false
        :rtype: bool
        """
        return self.get("selected", False)

    def getMusicInfoTag(self):
        """
        returns the MusicInfoTag for this item.
        """
        return None

    def getVideoInfoTag(self):
        """
        returns the VideoInfoTag for this item.
        """
        return None

    def setSubtitles(self, subtitleFiles):
        """
        Sets subtitles for this listitem.

        :param list subtitleFiles: - list of subtitle paths

        example::

            listitem.setSubtitles(['special://temp/example.srt', 'http://example.com/example.srt'])
        """
        self["subtitles"] = subtitleFiles

    def getdescription(self):
        """
        Returns the description of this PlayListItem.
        :rtype: str
        """
        return str()

    def getduration(self):
        """
        Returns the duration of this PlayListItem
        :rtype: str
        """
        return str()

    def getfilename(self):
        """
        Returns the filename of this PlayListItem.
        :rtype: str
        """
        return str()

    def select(self, selected):
        """
        Sets the listitem's selected status.

        :param selected: bool - True=selected/False=not selected.
        """
        self["selected"] = selected


# noinspection PyUnusedLocal, PyMethodMayBeStatic, PyShadowingBuiltins
class Dialog(object):
    """
    The graphical control element dialog box (also called dialogue box or just dialog)
    is a small window that communicates information to the user and prompts them for a response.
    """

    def browse(self, type, heading, shares, mask='', useThumbs=False, treatAsFolder=False,
               defaultt='', enableMultiple=False):
        """
        Show a 'Browse' dialog.

        :param int type: integer - the type of browse dialog.
        :param heading: string or unicode - dialog heading.
        :type heading: str or unicode

        :param shares: string or unicode - from sources.xml. (i.e. 'myprograms')
        :type shares: str or unicode

        :param mask: [opt] string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        :type mask: str or unicode

        :param bool useThumbs: [opt] boolean - if True autoswitch to Thumb view if files exist.
        :param bool treatAsFolder: [opt] boolean - if True playlists and archives act as folders.
        :param str defaultt: [opt] string - default path or file. Note the spelling of the argument name.
        :param bool enableMultiple: [opt] boolean - if True multiple file selection is enabled.
        :rtype: str

        Types::

            0: ShowAndGetDirectory
            1: ShowAndGetFile
            2: ShowAndGetImage
            3: ShowAndGetWriteableDirectory

        .. note::
            If enableMultiple is False (default): returns filename and/or path as a string
            to the location of the highlighted item, if user pressed 'Ok' or a masked item
            was selected. Returns the default value if dialog was canceled.

            If enableMultiple is True: returns tuple of marked filenames as a string,
            if user pressed 'Ok' or a masked item was selected. Returns empty tuple if dialog was canceled.

            If type is 0 or 3 the enableMultiple parameter is ignored.

        Example::

            dialog = xbmcgui.Dialog()
            fn = dialog.browse(3, 'XBMC', 'files', '', False, False, False, 'special://masterprofile/script_data/XBMC')
        """
        raise NotImplementedError("'Dialog.browse' is not implemented")

    def browseMultiple(self, type, heading, shares, mask='', useThumbs=None, treatAsFolder=None, defaultt=''):
        """
        Show a 'Browse' dialog.

        :param int type: integer - the type of browse dialog.

        :param heading: string or unicode - dialog heading.
        :type heading: str or unicode

        :param shares: string or unicode - from sources.xml. (i.e. 'myprograms')
        :type shares: str or unicode

        :param mask: [opt] string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        :type mask: str or unicode

        :param bool useThumbs: [opt] boolean - if True autoswitch to Thumb view if files exist (default=false).
        :param bool treatAsFolder: [opt] boolean - if True playlists and archives act as folders (default=false).
        :param str defaultt: [opt] string - default path or file. Note the spelling of the argument name.
        :rtype: tuple

        Types::

            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage


        .. note::
            Returns tuple of marked filenames as a string,
            if user pressed 'Ok' or a masked item was selected. Returns empty tuple if dialog was canceled.

        Example::

            dialog = xbmcgui.Dialog()
            fn = dialog.browseMultiple(2, 'XBMC', 'files', '', False, False, 'special://masterprofile/script_data/XBMC')
        """
        raise NotImplementedError("'Dialog.browseMultiple' is not implemented")

    def browseSingle(self, type, heading, shares, mask='', useThumbs=None, treatAsFolder=None, defaultt=''):
        """
        Show a 'Browse' dialog.

        :param int type: integer - the type of browse dialog.

        :param heading: string or unicode - dialog heading.
        :type heading: str or unicode

        :param shares: string or unicode - from sources.xml. (i.e. 'myprograms')
        :type shares: str or unicode

        :param mask: [opt] string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        :type mask: str or unicode

        :param bool useThumbs: [opt] boolean - if True autoswitch to Thumb view if files exist (default=false).
        :param bool treatAsFolder: [opt] boolean - if True playlists and archives act as folders (default=false).
        :param str defaultt: [opt] string - default path or file. Note the spelling of the argument name.
        :rtype: str

        Types::

            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory

        .. note:: Returns filename and/or path as a string to the location of the highlighted item,
            if user pressed 'Ok' or a masked item was selected.
            Returns the default value if dialog was canceled.

        Example::

            dialog = xbmcgui.Dialog()
            fn = dialog.browse(3, 'XBMC', 'files', '', False, False, 'special://masterprofile/script_data/XBMC Lyrics')
        """
        raise NotImplementedError("'Dialog.browseSingle' is not implemented")

    def input(self, heading, default="", type=INPUT_ALPHANUM, option=0, autoclose=0):
        """
        Show an Input dialog.

        :param str heading: string -- dialog heading.
        :param str default: [opt] string -- default value. (default=empty string)
        :param int type: [opt] integer -- the type of keyboard dialog. (default=xbmcgui.INPUT_ALPHANUM)
        :param int option: [opt] integer -- option for the dialog. (see Options below)
        :param int autoclose: [opt] integer -- milliseconds to autoclose dialog. (default=do not autoclose)
        :rtype: str

        Types:

        - xbmcgui.INPUT_ALPHANUM (standard keyboard)
        - xbmcgui.INPUT_NUMERIC (format: #)
        - xbmcgui.INPUT_DATE (format: DD/MM/YYYY)
        - xbmcgui.INPUT_TIME (format: HH:MM)
        - xbmcgui.INPUT_IPADDRESS (format: #.#.#.#)
        - xbmcgui.INPUT_PASSWORD (return md5 hash of input, input is masked)

        Options PasswordDialog: xbmcgui.PASSWORD_VERIFY (verifies an existing (default) md5 hashed password)
        Options AlphanumDialog: xbmcgui.ALPHANUM_HIDE_INPUT (masks input)

        .. note::
            Returns the entered data as a string.
            Returns an empty string if dialog was canceled.

        Example::

            dialog = xbmcgui.Dialog()
            d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        """
        print("#################")
        print("Input Dialog: %s" % heading)

        if type == 0:
            print("Expected format: Keyboard")
        elif type == 1:
            print("Expected format: Number, #")
        elif type == 2:
            print("Expected format: Date, DD/MM/YYYY")
        elif type == 3:
            print("Expected format: Time, HH:MM")
        elif type == 4:
            print("Expected format: IPAddress, #.#.#.#")
        else:
            print("Expected format: String")

        print("#################")

        try:
            # Password hash mode
            if type == INPUT_PASSWORD:
                if option == PASSWORD_VERIFY:
                    ret = _support.handle_prompt("Please enter password: ")
                    first_hash = _support.hash_password(ret)
                    if (default and default == first_hash) or (ret and not default):
                        return first_hash
                    else:
                        return ""
                else:
                    while True:
                        ret = _support.handle_prompt("Please enter password: ")
                        first_hash = _support.hash_password(ret)
                        ret = _support.handle_prompt("Please re-enter new password: ")
                        last_hash = _support.hash_password(ret)
                        if first_hash == last_hash:
                            if ret:
                                return first_hash
                            else:
                                return ""
                        else:
                            print("Passwords did not match")

            elif default:
                ret = _support.handle_prompt("Please enter text [%s]: ]" % default)
            else:
                ret = _support.handle_prompt("Please enter text: ")

        except(KeyboardInterrupt, EOFError):
            return ""
        else:
            if ret:
                return ret
            elif default:
                return default
            else:
                return ""

    def numeric(self, type, heading, default=''):
        """Show a 'Numeric' dialog.

        :param int type: integer -- the type of numeric dialog.

        :param heading: string or unicode -- dialog heading.
        :type heading: str or unicode

        :param str default: string -- default value.
        :rtype: str

        Types::

            0: ShowAndGetNumber    (default format: #)
            1: ShowAndGetDate      (default format: DD/MM/YYYY)
            2: ShowAndGetTime      (default format: HH:MM)
            3: ShowAndGetIPAddress (default format: #.#.#.#)

        .. note::
            Returns the entered data as a string.
            Returns the default value if dialog was canceled.

        Example::

            dialog = xbmcgui.Dialog()
            d = dialog.numeric(1, 'Enter date of birth')
        """
        return self.input(heading, default, type+1)

    def notification(self, heading, message, icon='', time=0, sound=True):
        """
        Show a Notification alert.

        :param str heading: string -- dialog heading.
        :param str message: string -- dialog message.
        :param str icon: [opt] string -- icon to use. (default xbmcgui.NOTIFICATION_INFO)
        :param int time: [opt] integer -- time in milliseconds (default 5000)
        :param bool sound: [opt] bool -- play notification sound (default True)

        Builtin Icons:

        - xbmcgui.NOTIFICATION_INFO
        - xbmcgui.NOTIFICATION_WARNING
        - xbmcgui.NOTIFICATION_ERROR

        example::

            dialog = xbmcgui.Dialog()
            dialog.notification('Movie Trailers', 'Finding Nemo download finished.', xbmcgui.NOTIFICATION_INFO, 5000)
        """
        print("Notification {}: {}".format(heading, message))

    def yesno(self, heading, line1, line2='', line3='', nolabel='', yeslabel='', autoclose=0):
        """
        Show a confirmation dialog 'YES/NO'.

        :param heading: string or unicode -- dialog heading.
        :type heading: str or unicode

        :param line1: string or unicode -- line #1 text.
        :type line1: str or unicode

        :param line2: [opt] string or unicode -- line #2 text.
        :type line2: str or unicode

        :param line3: [opt] string or unicode -- line #3 text.
        :type line3: str or unicode

        :param str nolabel: [opt] label to put on the no button.
        :param str yeslabel: [opt] label to put on the yes button.
        :param int autoclose : [opt] integer -- milliseconds to autoclose dialog. (default=do not autoclose)
        :rtype: bool

        .. note::
            Returns ``True`` if 'Yes' was pressed, else ``False``.

        Example::

            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('XBMC', 'Do you want to exit this script?')
        """
        print("#################")
        print("Yes/No Dialog: %s" % heading)
        print(line1)
        print(line2)
        print(line3)
        print("#################")
        print("No: %s" % nolabel)
        print("Yes: %s" % yeslabel)
        print("#################")

        try:
            ret = _support.handle_prompt("Please enter yes or no: ")
        except(KeyboardInterrupt, EOFError):
            return False
        else:
            ret = ret.lower()
            return ret == "yes" or ret == "y" or ret == "1"

    def ok(self, heading, line1, line2="", line3=""):
        """Show a dialog 'OK'.

        :param heading: string or unicode -- dialog heading.
        :type heading: str or unicode

        :param line1: string or unicode -- line #1 text.
        :type line1: str or unicode

        :param line2: [opt] string or unicode -- line #2 text.
        :type line2: str or unicode

        :param line3: [opt] string or unicode -- line #3 text.
        :type line3: str or unicode

        :rtype: bool

        .. note::
            Returns ``True`` if 'Ok' was pressed, else ``False``.

        Example::

            dialog = xbmcgui.Dialog()
            ok = dialog.ok('XBMC', 'There was an error.')
        """
        print("#############")
        print("OK Dialog %s" % heading)
        print(line1)
        print(line2)
        print(line3)
        print("#############")
        _support.handle_prompt("Please press enter to continue: ")
        return True

    def select(self, heading, list, autoclose=0, preselect=None, useDetails=False):
        """Show a select dialog.

        :param heading: string or unicode -- dialog heading.
        :type heading: str or unicode

        :param list list: string list -- list of items.
        :param int autoclose: [opt] integer -- milliseconds to autoclose dialog.
        :param int preselect: [opt] integer - index of preselected item. (default=no preselected item)
        :param bool useDetails: [opt] bool - use detailed list instead of a compact list. (default=false)

        :returns: Returns the position of the highlighted item as an integer.
        :rtype: int

        .. note::
            autoclose = 0 - This disables autoclose.
            Returns the position of the highlighted item as an integer.

        Example::

            dialog = xbmcgui.Dialog()
            ret = dialog.select('Choose a playlist', ['Playlist #1', 'Playlist #2, 'Playlist #3'])
        """
        print("#################")
        print("Select Dialog: %s" % heading)
        print("#################")
        for count, item in enumerate(list):
            if isinstance(item, ListItem):
                print("%s. %s" % (count, item.getLabel()))
            else:
                print("%s. %s" % (count, item))
        print("#################")

        try:
            ret = _support.handle_prompt("Please enter a selection 'id': ")
        except(KeyboardInterrupt, EOFError) as e:
            print(e)
            return preselect if preselect is not None else -1
        else:
            return int(ret)


# noinspection PyMethodMayBeStatic
class DialogProgress(object):
    """Kodi's progress dialog class (Duh!)."""

    def create(self, heading, line1='', line2='', line3=''):
        """Create and show a progress dialog.

        :param heading: string or unicode -- dialog heading.
        :type heading: str or unicode

        :param line1: string or unicode -- line #1 text.
        :type line1: str or unicode

        :param line2: string or unicode -- line #2 text.
        :type line2: str or unicode

        :param line3: string or unicode -- line #3 text.
        :type line3: str or unicode

        .. note::
            Use add() to add lines and progressbar.

        Example::

            pDialog = xbmcgui.DialogProgress()
            ret = pDialog.create('XBMC', 'Initializing script...')
        """
        pass

    def update(self, percent, line1='', line2='', line3=''):
        """Update's the progress dialog.

        :param int percent: integer - percent complete. (0:100)
        :param line1: string or unicode - line #1 text.
        :type line1: str or unicode

        :param line2: string or unicode - line #2 text.
        :type line1: str or unicode

        :param line3: string or unicode - line #3 text.
        :type line1: str or unicode

        .. note::
            If percent == 0, the progressbar will be hidden.

        Example::

            pDialog.add(25, 'Importing modules...')
        """
        pass

    def iscanceled(self):
        """
        Returns ``True`` if the user pressed cancel.
        :rtype: bool
        """
        return bool(1)

    def close(self):
        """Close the progress dialog."""
        pass


# noinspection PyPep8Naming, PyMethodMayBeStatic, PyUnusedLocal
class DialogProgressBG(object):
    """
    Kodi's background progress dialog class
    """
    def __init__(self):
        self._finished = False

    def close(self):
        """
        Close the background progress dialog

        example::

            pDialog.close()
        """
        pass

    def create(self, heading, message=''):
        """
        Create and show a background progress dialog.n

        :param heading: string or unicode - dialog heading
        :type heading: str or unicode

        :param message: [opt] string or unicode - message text
        :type message: str or unicode

        .. note:: 'heading' is used for the dialog's id. Use a unique heading.
            Use add() to add heading, message and progressbar.

        example::

            pDialog = xbmcgui.DialogProgressBG()
            pDialog.create('Movie Trailers', 'Downloading Monsters Inc. ...')
        """
        print("Creating background progress dialog box. Not.")

    def isFinished(self):
        """
        Returns ``True`` if the background dialog is active.
        :rtype: bool

        example::

            if (pDialog.isFinished()):
                break
        """
        return self._finished

    def update(self, percent=0, heading='', message=''):
        """
        Updates the background progress dialog.

        :param int percent: [opt] integer - percent complete. (0:100)
        :param heading: [opt] string or unicode - dialog heading
        :type heading: str or unicode

        :param message: [opt] string or unicode - message text
        :type message: str or unicode

        .. note:: To clear heading or message, you must pass a blank character.

        example::

            pDialog.add(25, message='Downloading Finding Nemo ...')
        """
        if percent >= 100:
            self._finished = True


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class Window(object):
    """
    Window(existingWindowId=-1)

    Create a new Window to draw on.

    Specify an id to use an existing window.

    :raises: ``ValueError``: If supplied window Id does not exist.
    :raises: ``Exception``: If more then 200 windows are created.

    Deleting this window will activate the old window that was active
    and resets (not delete) all controls that are associated with this window.
    """

    def __init__(self, existingWindowId=-1):
        pass

    def show(self):
        """Show this window.

        Shows this window by activating it, calling close() after it wil activate the current window again.

        .. note:: If your script ends this window will be closed to. To show it forever,
            make a loop at the end of your script and use ``doModal()`` instead.
        """
        pass

    def close(self):
        """Closes this window.

        Closes this window by activating the old window.
        The window is not deleted with this method.
        """
        pass

    def onAction(self, action):
        """onAction method.

        This method will recieve all actions that the main program will send to this window.
        By default, only the ``PREVIOUS_MENU`` action is handled.
        Overwrite this method to let your script handle all actions.

        Don't forget to capture ``ACTION_PREVIOUS_MENU``, else the user can't close this window.
        """
        pass

    def onClick(self, controlId):
        """onClick method.

        This method will recieve all click events that the main program will send to this window.
        """
        pass

    def onDoubleClick(self, controlId):
        """
        onClick method.

        This method will recieve all double click events that the main program will send
        to this window.
        """
        pass

    def onControl(self, control):
        """
        onControl method.

        This method will recieve all control events that the main program will send to this window.
        'control' is an instance of a Control object.
        """
        pass

    def onFocus(self, control):
        """onFocus method.

        This method will recieve all focus events that the main program will send to this window.
        """
        pass

    def onInit(self):
        """onInit method.

        This method will be called to initialize the window.
        """
        pass

    def doModal(self):
        """Display this window until ``close()`` is called."""
        pass

    def addControl(self, pControl):
        """Add a Control to this window.

        :raises: ``TypeError``: If supplied argument is not a Control type.
        :raises: ``ReferenceError``: If control is already used in another window.
        :raises: ``RuntimeError``: Should not happen :-)

        The next controls can be added to a window atm:

            * ``ControlLabel``
            * ``ControlFadeLabel``
            * ``ControlTextBox``
            * ``ControlButton``
            * ``ControlCheckMark``
            * ``ControlList``
            * ``ControlGroup``
            * ``ControlImage``
            * ``ControlRadioButton``
            * ``ControlProgress``
        """
        pass

    def addControls(self, pControls):
        """
        Add a list of Controls to this window.

        :raises: ``TypeError``, if supplied argument is not ofList type, or a control is not ofControl type
        :raises: ``ReferenceError``, if control is already used in another window
        :raises: ``RuntimeError``, should not happen :-)
        """
        pass

    def getControl(self, iControlId):
        """Get's the control from this window.

        :raises: ``Exception``: If Control doesn't exist

        controlId doesn't have to be a python control, it can be a control id
        from a xbmc window too (you can find id's in the xml files).

        .. note:: Non-Python controls are not completely usable yet.
            You can only use the ``Control`` functions.
        """
        return Control()

    def setFocus(self, pControl):
        """Give the supplied control focus.

        :raises: ``TypeError``: If supplied argument is not a Control type.
        :raises: ``SystemError``: On Internal error.
        :raises: ``RuntimeError``: If control is not added to a window.
        """
        pass

    def setFocusId(self, iControlId):
        """Gives the control with the supplied focus.

        :raises: ``SystemError``: On Internal error.
        :raises: ``RuntimeError``: If control is not added to a window.
        """
        pass

    def getFocus(self):
        """Returns the control which is focused.

        :raises: ``SystemError``: On Internal error.
        :raises: ``RuntimeError``: If no control has focus.
        """
        return Control

    def getFocusId(self):
        """Returns the id of the control which is focused.

        :raises: ``SystemError``: On Internal error.
        :raises: ``RuntimeError``: If no control has focus.
        """
        return _support.long_type()

    def removeControl(self, pControl):
        """Removes the control from this window.

        :raises: ``TypeError``: If supplied argument is not a Control type.
        :raises: ``RuntimeError``: If control is not added to this window.

        This will not delete the control. It is only removed from the window.
        """
        pass

    def removeControls(self, pControls):
        """
        removeControls(self, List)--Removes a list of controls from this window.

        :raises: ``TypeError``, if supplied argument is not aControl type
        :raises: ``RuntimeError``, if control is not added to this window

        This will not delete the controls. They are only removed from the window.
        """
        pass

    def getHeight(self):
        """Returns the height of this screen."""
        return _support.long_type()

    def getWidth(self):
        """Returns the width of this screen."""
        return _support.long_type()

    def getResolution(self):
        """Returns the resolution of the screen.

        The returned value is one of the following:

        * RES_INVALID        = -1,
        * RES_HDTV_1080i     =  0,
        * RES_HDTV_720pSBS   =  1,
        * RES_HDTV_720pTB    =  2,
        * RES_HDTV_1080pSBS  =  3,
        * RES_HDTV_1080pTB   =  4,
        * RES_HDTV_720p      =  5,
        * RES_HDTV_480p_4x3  =  6,
        * RES_HDTV_480p_16x9 =  7,
        * RES_NTSC_4x3       =  8,
        * RES_NTSC_16x9      =  9,
        * RES_PAL_4x3        = 10,
        * RES_PAL_16x9       = 11,
        * RES_PAL60_4x3      = 12,
        * RES_PAL60_16x9     = 13,
        * RES_AUTORES        = 14,
        * RES_WINDOW         = 15,
        * RES_DESKTOP        = 16,  Desktop resolution for primary screen
        * RES_CUSTOM         = 16 + 1

        See: https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Resolution.h
        """
        return _support.long_type()

    def setCoordinateResolution(self, res):
        """Sets the resolution that the coordinates of all controls are defined in.

        Allows XBMC to scale control positions and width/heights to whatever resolution
        XBMC is currently using.

        resolution is one of the following:

        * RES_INVALID        = -1,
        * RES_HDTV_1080i     =  0,
        * RES_HDTV_720pSBS   =  1,
        * RES_HDTV_720pTB    =  2,
        * RES_HDTV_1080pSBS  =  3,
        * RES_HDTV_1080pTB   =  4,
        * RES_HDTV_720p      =  5,
        * RES_HDTV_480p_4x3  =  6,
        * RES_HDTV_480p_16x9 =  7,
        * RES_NTSC_4x3       =  8,
        * RES_NTSC_16x9      =  9,
        * RES_PAL_4x3        = 10,
        * RES_PAL_16x9       = 11,
        * RES_PAL60_4x3      = 12,
        * RES_PAL60_16x9     = 13,
        * RES_AUTORES        = 14,
        * RES_WINDOW         = 15,
        * RES_DESKTOP        = 16,  Desktop resolution for primary screen
        * RES_CUSTOM         = 16 + 1

        See: https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Resolution.h
        """
        pass

    def setProperty(self, key, value):
        """Sets a window property, similar to an infolabel.

        :param key: string - property name.
        :param value: string or unicode - value of property.

        .. note:: key is NOT case sensitive. Setting value to an empty string is equivalent to clearProperty(key).

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.setProperty('Category', 'Newest')
        """
        pass

    def getProperty(self, key):
        """Returns a window property as a string, similar to an infolabel.

        :param key: string - property name.

        .. note:: key is NOT case sensitive.

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            category = win.getProperty('Category')
        """
        return str()

    def clearProperty(self, key):
        """Clears the specific window property.

        :param key: string - property name.

        .. note:: key is NOT case sensitive. Equivalent to setProperty(key,'').

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.clearProperty('Category')
        """
        pass

    def clearProperties(self):
        """Clears all window properties.

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.clearProperties()
        """
        pass


class WindowDialog(Window):
    """
    WindowDialog()

    Create a new WindowDialog with transparent background.

    Unlike Window, WindowDialog always stays on top of XBMC UI.
    """
    pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class WindowXML(Window):
    """
    WindowXML(xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p')

    WindowXML class.

    :param xmlFilename: string - the name of the xml file to look for.
    :param: scriptPath: string - path to script. used to fallback to if the xml doesn't exist in the current skin.
        (eg ``os.getcwd()``)
    :param defaultSkin: string - name of the folder in the skins path to look in for the xml.
    :param defaultRes: string - default skins resolution.

    .. note:: Skin folder structure is eg (resources/skins/Default/720p).

    Example::

        ui = WindowXML('script-Lyrics-main.xml', os.getcwd(), 'LCARS', 'PAL')
        ui.doModal()
        del ui
    """

    def __init__(self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p'):
        super(WindowXML, self).__init__()
        pass

    def removeItem(self, position):
        """Removes a specified item based on position, from the Window List.

        :param position: integer - position of item to remove.
        """
        pass

    def addItem(self, item, position=32767):
        """Add a new item to this Window List.

        :param item: string, unicode or ListItem - item to add.
        :param position: integer - position of item to add.
            (NO Int = Adds to bottom,0 adds to top, 1 adds to one below from top,-1 adds to one above from bottom etc)
            If integer positions are greater than list size, negative positions will add to top of list,
            positive positions will add to bottom of list.

        Example::

            self.addItem('Reboot XBMC', 0)
        """
        pass

    def clearList(self):
        """Clear the Window List."""
        pass

    def setCurrentListPosition(self, position):
        """Set the current position in the Window List.

        :param position: integer - position of item to set.
        """
        pass

    def getCurrentListPosition(self):
        """Gets the current position in the Window List."""
        return int()

    def getListItem(self, position):
        """Returns a given ListItem in this Window List.

        :param position: integer - position of item to return.
        """
        return ListItem()

    def getListSize(self):
        """Returns the number of items in this Window List."""
        return int()

    def setProperty(self, strProperty, strValue):
        """Sets a container property, similar to an infolabel.

        :param strProperty: string - property name.
        :param strValue: string or unicode - value of property.

        .. note:: ``strProperty`` is NOT case sensitive.

        Example::

            self.setProperty('Category', 'Newest')
        """
        pass


class WindowXMLDialog(WindowXML):
    """
    WindowXMLDialog(xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p')

    WindowXMLDialog class.

    :param xmlFilename: string - the name of the xml file to look for.
    :param: scriptPath: string - path to script. used to fallback to if the xml doesn't exist in the current skin.
        (eg ``os.getcwd()``)
    :param defaultSkin: string - name of the folder in the skins path to look in for the xml.
    :param defaultRes: string - default skins resolution.

    .. note:: Skin folder structure is eg (resources/skins/Default/720p).

    Example::

        ui = WindowXMLDialog('script-Lyrics-main.xml', os.getcwd(), 'LCARS', 'PAL')
        ui.doModal()
        del ui
    """
    def __init__(self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p'):
        super(WindowXMLDialog, self).__init__(xmlFilename, scriptPath, defaultSkin, defaultRes)


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class Control(object):
    """
    Parent for control classes.

    The problem here is that Python uses references to this class in a dynamic typing way.
    For example, you will find this type of python code frequently::

    window.getControl( 100 ).setLabel( "Stupid Dynamic Type")

    Notice that the 'getControl' call returns a 'Control ' object.

    In a dynamically typed language, the subsequent call to setLabel works if the specific type of control has method.
    The script writer is often in a position to know more than the code about the specificControl type
    (in the example, that control id 100 is a 'ControlLabel ') where the C++ code is not.

    SWIG doesn't support this type of dynamic typing. The 'Control ' wrapper that's returned will wrap aControlLabel
    but will not have the 'setLabel' method on it. The only way to handle this is to add all possible subclass methods
    to the parent class. This is ugly but the alternative is nearly as ugly.
    It's particularly ugly here because the majority of the methods are unique to the particular subclass.

    If anyone thinks they have a solution then let me know. The alternative would be to have a set of 'getContol'
    methods, each one coresponding to a type so that the downcast can be done in the native code.

    IOW rather than a simple 'getControl' there would be a 'getControlLabel', 'getControlRadioButton',
    'getControlButton', etc.

    TODO: This later solution should be implemented for future scripting languages
    while the former will remain as deprecated functionality for Python.
    """
    def addItem(self):
        pass

    def addItems(self):
        pass

    def canAcceptMessages(self):
        pass

    def controlDown(self, control):
        """
        Set's the controls down navigation.

        :param control: control object - control to navigate to on down.

        .. note:: You can also usesetNavigation() . Set to self to disable navigation.

        :raises: TypeError, if one of the supplied arguments is not a control type.
        :raises: ReferenceError, if one of the controls is not added to a window.

        example::

            self.button.controlDown(self.button1)
        """
        pass

    def controlLeft(self, control):
        """
        Set's the controls left navigation.

        :param control: control object - control to navigate to on left.

        .. note:: You can also usesetNavigation(). Set to self to disable navigation.

        :raises: TypeError, if one of the supplied arguments is not a control type.
        :raises: ReferenceError, if one of the controls is not added to a window.

        example::

            self.button.controlLeft(self.button1)
        """
        pass

    def controlRight(self, control):
        """
        Set's the controls right navigation.

        :param control: control object - control to navigate to on right.

        .. note:: You can also usesetNavigation(). Set to self to disable navigation.

        :raises: TypeError, if one of the supplied arguments is not a control type.
        :raises: ReferenceError, if one of the controls is not added to a window.

        example::

            self.button.controlRight(self.button1)
        """
        pass

    def controlUp(self, control):
        """
        Set's the controls up navigation.

        :param control: control object - control to navigate to on up.

        .. note:: You can also usesetNavigation() . Set to self to disable navigation.

        :raises: TypeError, if one of the supplied arguments is not a control type.
        :raises: ReferenceError, if one of the controls is not added to a window.

        example::

            self.button.controlUp(self.button1)
         """
        pass

    def getHeight(self):
        """
        Returns the control's current height as an integer.

        example::

            height = self.button.getHeight()
        """
        return _support.long_type()

    def getId(self):
        """
        Returns the control's current id as an integer.

        example::

            id = self.button.getId()
        """
        return _support.long_type()

    def getPosition(self):
        """
        Returns the control's current position as a x,y integer tuple.

        example::

            pos = self.button.getPosition()
        """
        return _support.long_type(), _support.long_type()

    def getWidth(self):
        """
        Returns the control's current width as an integer.

        example::

            width = self.button.getWidth()
        """
        return _support.long_type()

    def getX(self):
        """
        Get X coordinate of a control as an integer.
        """
        return _support.long_type()

    def getY(self):
        """
        Get Y coordinate of a control as an integer.
        """
        return _support.long_type()

    def setAnimations(self, eventAttr):
        """
        Set's the control's animations.

        :param eventAttr: list -- A list of tuples [(event,attr,)*] consisting of event and attributes pairs.

        ``event`` : string - The event to animate.
        ``attr`` : string - The whole attribute string separated by spaces.

        Animating your skin -http://wiki.xbmc.org/?title=Animating_Your_Skin

        example::

            self.button.setAnimations([('focus', 'effect=zoom end=90,247,220,56 time=0',)])
        """
        pass

    def setEnableCondition(self, enable):
        """
        Set's the control's enabled condition.

        Allows XBMC to control the enabled status of the control.

        :param enable: string - Enable condition.

        List of Conditions: http://wiki.xbmc.org/index.php?title=List_of_Boolean_Conditions

        example::

            self.button.setEnableCondition('System.InternetState')
        """
        pass

    def setEnabled(self, enabled):
        """
        Set's the control's enabled/disabled state.

        :param enabled: bool - True=enabled / False=disabled.

        example::

            self.button.setEnabled(False)
        """
        pass

    def setHeight(self, height):
        """
        Set's the controls height.

        :param height: integer - height of control.

        example::

            self.image.setHeight(100)
        """
        pass

    def setNavigation(self, up, down, left, right):
        """
        Set's the controls navigation.

        :param up: control object - control to navigate to on up.
        :param down: control object - control to navigate to on down.
        :param left: control object - control to navigate to on left.
        :param right: control object - control to navigate to on right.

        .. note:: Same ascontrolUp() ,controlDown() ,controlLeft() ,controlRight().
            Set to self to disable navigation for that direction.

        :raises: TypeError, if one of the supplied arguments is not a control type.
        :raises: ReferenceError, if one of the controls is not added to a window.

        example::

            self.button.setNavigation(self.button1, self.button2, self.button3, self.button4)
        """
        pass

    def setPosition(self, x, y):
        """
        Set's the controls position.

        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.

        .. note:: You may use negative integers. (e.g sliding a control into view)

        example::

            self.button.setPosition(100, 250)
        """
        pass

    def setVisible(self, visible):
        """
        Set's the control's visible/hidden state.

        :param visible: bool - True=visible / False=hidden.

        example::

            self.button.setVisible(False)
        """
        pass

    def setVisibleCondition(self, condition, allowHiddenFocus=False):
        """
        Set's the control's visible condition.

        Allows XBMC to control the visible status of the control.

        :param condition: string - Visible condition.
        :param allowHiddenFocus: bool - True=gains focus even if hidden.

        List of Conditions: http://wiki.xbmc.org/index.php?title=List_of_Boolean_Conditions

        example::

            self.button.setVisibleCondition('[Control.IsVisible(41) + !Control.IsVisible(12)]', True)
        """
        pass

    def setWidth(self, width):
        """
        Set's the controls width.

        :param width: integer - width of control.

        example::

            self.image.setWidth(100)
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlLabel(Control):
    """
    ControlLabel(x, y, width, height, label, font=None, textColor=None, disabledColor=None,
                 alignment=0, hasPath=False, angle=0)

    ControlLabel class.

    Creates a text label.

    :param x: integer -- x coordinate of control.
    :param y: integer -- y coordinate of control.
    :param width: integer -- width of control.
    :param height: integer -- height of control.
    :param label: string or unicode -- text string.
    :param font: string -- font used for label text. (e.g. 'font13')
    :param textColor: hexstring -- color of enabled label's label. (e.g. '0xFFFFFFFF')
    :param disabledColor: hexstring -- color of disabled label's label. (e.g. '0xFFFF3300')
    :param alignment: integer -- alignment of label -- *Note, see xbfont.h
    :param hasPath: bool -- True=stores a path / False=no path.
    :param angle: integer -- angle of control. (+ rotates CCW, - rotates CW)

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.label = xbmcgui.ControlLabel(100, 250, 125, 75, 'Status', angle=45)
    """

    def __init__(self, x, y, width, height, label,
                 font=None, textColor=None, disabledColor=None, alignment=0,
                 hasPath=False, angle=0):
        pass

    def setLabel(self, label='', font=None, textColor=None, disabledColor=None, shadowColor=None,
                 focusedColor=None, label2=''):
        """Set's text for this label.

        :param label: [opt] string or unicode - text string.
        :param font: [opt] string - font used for label text. (e.g. 'font13')
        :param textColor: [opt] hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: [opt] hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
        :param shadowColor: [opt] hexstring - color of button's label's shadow. (e.g. '0xFF000000')
        :param focusedColor: [opt] hexstring - color of focused button's label. (e.g. '0xFF00FFFF')
        :param label2: [opt] string or unicode - text string.
        """
        pass

    def getLabel(self):
        """Returns the text value for this label."""
        return _support.unicode_type()


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlFadeLabel(Control):
    """
    ControlFadeLabel(x, y, width, height, font=None, textColor=None, _alignment=0)

    Control which scrolls long label text.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param font: string - font used for label text. (e.g. 'font13')
    :param textColor: hexstring - color of fadelabel's labels. (e.g. '0xFFFFFFFF')
    :param _alignment: integer - alignment of label - *Note, see xbfont.h

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.fadelabel = xbmcgui.ControlFadeLabel(100, 250, 200, 50, textColor='0xFFFFFFFF')
    """

    def __init__(self, x, y, width, height, font=None, textColor=None, _alignment=0):
        pass

    def addLabel(self, label):
        """Add a label to this control for scrolling.

        :param label: string or unicode - text string.
        """
        pass

    def reset(self):
        """Clears this fadelabel."""
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlTextBox(Control):

    """
    ControlTextBox(x, y, width, height, font=None, textColor=None)

    ControlTextBox class.

    Creates a box for multi-line text.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param font: string - font used for text. (e.g. 'font13')
    :param textColor: hexstring - color of textbox's text. (e.g. '0xFFFFFFFF')

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.textbox = xbmcgui.ControlTextBox(100, 250, 300, 300, textColor='0xFFFFFFFF')
    """

    def __init__(self, x, y, width, height, font=None, textColor=None):
        pass

    def autoScroll(self, delay, time, repeat):
        """
        Set autoscrolling times.

        :param delay: integer - Scroll delay (in ms)
        :param time: integer - Scroll time (in ms)
        :param repeat: integer - Repeat time

        example::

            self.textbox.autoScroll(1, 2, 1)
        """
        pass

    def getText(self):
        """
        Returns the text value for this textbox.

        example::

            text = self.text.getText()
        """
        return _support.unicode_type()

    def setText(self, text):
        """Set's the text for this textbox.

        :param text: string or unicode - text string.
        """
        pass

    def scroll(self, id):
        """Scrolls to the given position.

        :param id: integer - position to scroll to.
        """
        pass

    def reset(self):
        """Clear's this textbox."""
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlButton(Control):
    """
    ControlButton(x, y, width, height, label, focusTexture=None, noFocusTexture=None,
                  textOffsetX=CONTROL_TEXT_OFFSET_X, textOffsetY=CONTROL_TEXT_OFFSET_Y,
                  alignment=4, font=None, textColor=None, disabledColor=None, angle=0,
                  shadowColor=None, focusedColor=None)

    ControlButton class.

    Creates a clickable button.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param label: string or unicode - text string.
    :param focusTexture: string - filename for focus texture.
    :param noFocusTexture: string - filename for no focus texture.
    :param textOffsetX: integer - x offset of label.
    :param textOffsetY: integer - y offset of label.
    :param alignment: integer - alignment of label - *Note, see xbfont.h
    :param font: string - font used for label text. (e.g. 'font13')
    :param textColor: hexstring - color of enabled button's label. (e.g. '0xFFFFFFFF')
    :param disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
    :param angle: integer - angle of control. (+ rotates CCW, - rotates CW)
    :param shadowColor: hexstring - color of button's label's shadow. (e.g. '0xFF000000')
    :param focusedColor: hexstring - color of focused button's label. (e.g. '0xFF00FFFF')

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.button = xbmcgui.ControlButton(100, 250, 200, 50, 'Status', font='font14')
    """

    def __init__(self, x, y, width, height, label, focusTexture=None, noFocusTexture=None,
                 textOffsetX=CONTROL_TEXT_OFFSET_X,
                 textOffsetY=CONTROL_TEXT_OFFSET_Y,
                 alignment=4,
                 font=None, textColor=None, disabledColor=None, angle=0,
                 shadowColor=None, focusedColor=None):
        pass

    def setDisabledColor(self, color):
        """Set's this buttons disabled color.

        :param color: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        """
        pass

    def setLabel(self, label='', font=None, textColor=None, disabledColor=None, shadowColor=None,
                 focusedColor=None, label2=''):
        """Set's this buttons text attributes.

        :param label: string or unicode - text string.
        :param font: string - font used for label text. (e.g. 'font13')
        :param textColor: hexstring - color of enabled button's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        :param shadowColor: hexstring - color of button's label's shadow. (e.g. '0xFF000000')
        :param focusedColor: hexstring - color of focused button's label. (e.g. '0xFFFFFF00')
        :param label2: string or unicode - text string.

        Example::

            self.button.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')
        """
        pass

    def getLabel(self):
        """Returns the buttons label as a unicode string."""
        return _support.unicode_type()

    def getLabel2(self):
        """Returns the buttons label2 as a unicode string."""
        return _support.unicode_type()


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlCheckMark(Control):

    """
    ControlCheckMark(x, y, width, height, label, focusTexture=None, noFocusTexture=None, checkWidth=30,
                     checkHeight=30, _alignment=1, font=None, textColor=None, disabledColor=None)

    ControlCheckMark class.

    Creates a checkmark with 2 states.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param label: string or unicode - text string.
    :param focusTexture: string - filename for focus texture.
    :param noFocusTexture: string - filename for no focus texture.
    :param checkWidth: integer - width of checkmark.
    :param checkHeight: integer - height of checkmark.
    :param _alignment: integer - alignment of label - *Note, see xbfont.h
    :param font: string - font used for label text. (e.g. 'font13')
    :param textColor: hexstring - color of enabled checkmark's label. (e.g. '0xFFFFFFFF')
    :param disabledColor: hexstring - color of disabled checkmark's label. (e.g. '0xFFFF3300')

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.checkmark = xbmcgui.ControlCheckMark(100, 250, 200, 50, 'Status', font='font14')
    """

    def __init__(self, x, y, width, height, label,
                 focusTexture=None, noFocusTexture=None, checkWidth=30,
                 checkHeight=30, _alignment=1, font=None, textColor=None, disabledColor=None):
        pass

    def setDisabledColor(self, color):
        """Set's this controls disabled color.

        :param color: hexstring - color of disabled checkmark's label. (e.g. '0xFFFF3300')
        """
        pass

    def setLabel(self, label='', font=None, textColor=None, disabledColor=None,
                 shadowColor=None, focusedColor=None, label2=''):
        """Set's this controls text attributes.

        :param label: string or unicode - text string.
        :param font: string - font used for label text. (e.g. 'font13')
        :param textColor: hexstring - color of enabled checkmark's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: hexstring - color of disabled checkmark's label. (e.g. '0xFFFF3300')
        :param shadowColor: hexstring - color of shadow label. (e.g. '0xFFFF3300')
        :param focusedColor: hexstring - color of focused label. (e.g. '0xFFFF3300')
        :param label2: string - label2

        Example::

            self.checkmark.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300')
        """
        pass

    def getSelected(self):
        """Returns the selected status for this checkmark as a bool."""
        return bool(1)

    def setSelected(self, selected):
        """Sets this checkmark status to on or off.

        :param selected: bool - True=selected (on) / False=not selected (off)
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic, PyMethodOverriding
class ControlList(Control):

    """
    ControlList(x, y, width, height, font=None, textColor=None, buttonTexture=None, buttonFocusTexture=None,
                selectedColor=None, _imageWidth=10, _imageHeight=10, _itemTextXOffset=10, _itemTextYOffset=2,
                _itemHeight=27, _space=2, _alignmentY=4)

    ControlList class.

    Creates a list of items.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param font: string - font used for items label. (e.g. 'font13')
    :param textColor: hexstring - color of items label. (e.g. '0xFFFFFFFF')
    :param buttonTexture: string - filename for no focus texture.
    :param buttonFocusTexture: string - filename for focus texture.
    :param selectedColor: integer - x offset of label.
    :param _imageWidth: integer - width of items icon or thumbnail.
    :param _imageHeight: integer - height of items icon or thumbnail.
    :param _itemTextXOffset: integer - x offset of items label.
    :param _itemTextYOffset: integer - y offset of items label.
    :param _itemHeight: integer - height of items.
    :param _space: integer - space between items.
    :param _alignmentY: integer - Y-axis alignment of items label - *Note, see xbfont.h

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.cList = xbmcgui.ControlList(100, 250, 200, 250, 'font14', _space=5)
    """

    def __init__(self, x, y, width, height, font=None, textColor=None, buttonTexture=None,
                 buttonFocusTexture=None, selectedColor=None, _imageWidth=10, _imageHeight=10,
                 _itemTextXOffset=10, _itemTextYOffset=2,
                 _itemHeight=27, _space=2, _alignmentY=4):
        pass

    def addItem(self, item):
        """Add a new item to this list control.

        :param item: string, unicode or ListItem - item to add.
        """
        pass

    def addItems(self, items):
        """Adds a list of listitems or strings to this list control.

        :param items: List - list of strings, unicode objects or ListItems to add.
        """
        pass

    def selectItem(self, item):
        """Select an item by index number.

        :param item: integer - index number of the item to select.
        """
        pass

    def reset(self):
        """Clear all ListItems in this control list."""
        pass

    def getSpinControl(self):
        """Returns the associated ControlSpin object.

        .. warning:: Not working completely yet.
            After adding this control list to a window it is not possible to change
            the settings of this spin control.
        """
        return ControlSpin()

    def setImageDimensions(self, imageWidth, imageHeight):
        """Sets the width/height of items icon or thumbnail.

        :param imageWidth: integer - width of items icon or thumbnail.
        :param imageHeight: integer - height of items icon or thumbnail.
        """
        pass

    def setItemHeight(self, itemHeight):
        """Sets the height of items.

        :param itemHeight: integer - height of items.
        """
        pass

    def setPageControlVisible(self, visible):
        """Sets the spin control's visible/hidden state.

        :param visible: boolean - True=visible / False=hidden.
        """
        pass

    def setSpace(self, space):
        """Set's the space between items.

        :param space: integer - space between items.
        """
        pass

    def getSelectedPosition(self):
        """Returns the position of the selected item as an integer.

        .. note:: Returns ``-1`` for empty lists.
        """
        return _support.long_type()

    def getSelectedItem(self):
        """Returns the selected item as a ListItem object.

       .. note:: Same as ``getSelectedPosition()``, but instead of an integer a ``ListItem`` object is returned.
            Returns ``None`` for empty lists.
        """
        return ListItem()

    def size(self):
        """Returns the total number of items in this list control as an integer."""
        return _support.long_type()

    def getListItem(self, index):
        """Returns a given ListItem in this List.

        :param index: integer - index number of item to return.

        :raises ValueError: If index is out of range.
        """
        return ListItem()

    def getItemHeight(self):
        """Returns the control's current item height as an integer."""
        return _support.long_type()

    def getSpace(self):
        """Returns the control's space between items as an integer."""
        return _support.long_type()

    def setStaticContent(self, items):
        """Fills a static list with a list of listitems.

        :param items: List - list of listitems to add.
        """
        pass

    def removeItem(self, index):
        """
        Remove an item by index number.

        :param index: integer - index number of the item to remove.

        example::

            my_list.removeItem(12)
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlImage(Control):
    """
    ControlImage(x, y, width, height, filename, aspectRatio=0, colorDiffuse=None)

    ControlImage class.

    Displays an image from a file.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param filename: string - image filename.
    :param aspectRatio: integer - (values 0 = stretch (default), 1 = scale up (crops), 2 = scale down (black bars)
    :param colorDiffuse: hexString - (example, '0xC0FF0000' (red tint)).

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.image = xbmcgui.ControlImage(100, 250, 125, 75, aspectRatio=2)
    """

    def __init__(self, x, y, width, height, filename, aspectRatio=0, colorDiffuse=None):
        pass

    def setImage(self, imageFilename, useCache=True):
        """Changes the image.

        :param imageFilename: string - image filename.
        :param useCache: [opt] bool - True=use cache (default) / False=don't use cache.
        """
        pass

    def setColorDiffuse(self, hexString):
        """Changes the images color.

        :param hexString: - example -- '0xC0FF0000' (red tint).
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlProgress(Control):

    """
    ControlProgress(self, x, y, width, height, texturebg=None, textureleft=None,
                    texturemid=None, textureright=None, textureoverlay=None)

    ControlProgress class.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param texturebg: string - image filename.
    :param textureleft: string - image filename.
    :param texturemid: string - image filename.
    :param textureright: string - image filename.
    :param textureoverlay: string - image filename.

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.progress = xbmcgui.ControlProgress(100, 250, 125, 75)

    .. warning::
        This control seems to be broken. At least I couldn't make it work (Roman V.M.).
    """

    def __init__(self, x, y, width, height,
                 texturebg=None, textureleft=None,
                 texturemid=None, textureright=None,
                 textureoverlay=None):
        pass

    def setPercent(self, pct):
        """Sets the percentage of the progressbar to show.

        :param pct: float - percentage of the bar to show.

        .. note::
            Valid range for percent is 0-100.
        """
        pass

    def getPercent(self):
        """Returns a float of the percent of the progress."""
        return float()


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlSlider(Control):
    """
    ControlSlider(x, y, width, height, textureback=None, texture=None, texturefocus=None)

    ControlSlider class.

    Creates a slider.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param textureback: string - image filename.
    :param texture: string - image filename.
    :param texturefocus: string - image filename.

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.slider = xbmcgui.ControlSlider(100, 250, 350, 40)
    """

    def __init__(self, x, y, width, height, textureback=None, texture=None, texturefocus=None):
        pass

    def getPercent(self):
        """Returns a float of the percent of the slider."""
        return float()

    def setPercent(self, percent):
        """Sets the percent of the slider.

        :param percent: float -- slider % value
        """
        pass


# noinspection PyUnusedLocal
class ControlGroup(Control):

    """
    ControlGroup(x, y, width, height)

    ControlGroup class.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.

    Example::

        self.group = xbmcgui.ControlGroup(100, 250, 125, 75)
    """

    def __init__(self, x, y, width, height):
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlEdit(Control):

    """
    ControlEdit(self, x, y, width, height, label, font=None, textColor=None, disabledColor=None,
                _alignment=0, focusTexture=None, noFocusTexture=None, isPassword=False)

    ControlEdit class.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param label: string or unicode - text string.
    :param font: [opt] string - font used for label text. (e.g. 'font13')
    :param textColor: [opt] hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
    :param disabledColor: [opt] hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
    :param _alignment: [opt] integer - alignment of label - *Note, see xbfont.h
    :param focusTexture: [opt] string - filename for focus texture.
    :param noFocusTexture: [opt] string - filename for no focus texture.
    :param isPassword: [opt] bool - if true, mask text value.

    .. note::
        You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.
        After you create the control, you need to add it to the window with ``addControl()``.

    Example::

        self.edit = xbmcgui.ControlEdit(100, 250, 125, 75, 'Status')
    """

    def __init__(self, x, y, width, height, label, font=None, textColor=None,
                 disabledColor=None, _alignment=0,
                 focusTexture=None, noFocusTexture=None, isPassword=False):
        pass

    def getLabel(self):
        """
       Returns the text heading for this edit control.

        example::

            label = self.edit.getLabel()
        """
        return _support.unicode_type()

    def getText(self):
        """
        Returns the text value for this edit control.

        example::

            value = self.edit.getText()
        """
        return _support.unicode_type()

    def setLabel(self, label='', font=None, textColor=None, disabledColor=None, shadowColor=None,
                 focusedColor=None, label2=''):
        """
        Set's text heading for this edit control.

        :param label: string or unicode - text string.
        :param font: [opt] string - font used for label text. (e.g. 'font13')
        :param textColor: [opt] hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: [opt] hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
        :param shadowColor: [opt] hexstring - color of button's label's shadow. (e.g. '0xFF000000')
        :param focusedColor: [opt] hexstring - color of focused button's label. (e.g. '0xFF00FFFF')
        :param label2: [opt] string or unicode - text string.

        example::

            self.edit.setLabel('Status')
        """
        pass

    def setText(self, text):
        """
        Set's text value for this edit control.

        :param text: - string or unicode - text string.

        example::

            self.edit.longsetText('online')
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlRadioButton(Control):

    """
    ControlRadioButton class.
    Creates a radio-button with 2 states.
    """

    def __init__(self, x, y, width, height, label, focusTexture=None, noFocusTexture=None, textOffsetX=None,
                 textOffsetY=None, _alignment=None, font=None, textColor=None, disabledColor=None, angle=None,
                 shadowColor=None, focusedColor=None, focusOnTexture=None, noFocusOnTexture=None,
                 focusOffTexture=None, noFocusOffTexture=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        label: string or unicode - text string.
        focusTexture: string - filename for focus texture.
        noFocusTexture: string - filename for no focus texture.
        textOffsetX: integer - x offset of label.
        textOffsetY: integer - y offset of label.
        _alignment: integer - alignment of label - *Note, see xbfont.h
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled radio button's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled radio button's label. (e.g. '0xFFFF3300')
        angle: integer - angle of control. (+ rotates CCW, - rotates CW)
        shadowColor: hexstring - color of radio button's label's shadow. (e.g. '0xFF000000')
        focusedColor: hexstring - color of focused radio button's label. (e.g. '0xFF00FFFF')
        focusOnTexture: string - filename for radio focused/checked texture.
        noFocusOnTexture: string - filename for radio not focused/checked texture.
        focusOffTexture: string - filename for radio focused/unchecked texture.
        noFocusOffTexture: string - filename for radio not focused/unchecked texture.
        Note: To customize RadioButton all 4 abovementioned textures need to be provided.
        focus and noFocus textures can be the same.

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.radiobutton = xbmcgui.ControlRadioButton(100, 250, 200, 50, 'Status', font='font14')
        """
        pass

    def setSelected(self, selected):
        """Sets the radio buttons's selected status.

        :param selected: bool - True=selected (on) / False=not selected (off)
        """
        pass

    def isSelected(self):
        """Returns the radio buttons's selected status."""
        return bool(1)

    def setLabel(self, label, font=None, textColor=None, disabledColor=None, shadowColor=None, focusedColor=None):
        """Set's the radio buttons text attributes.

        :param label: string or unicode - text string.
        :param font: string - font used for label text. (e.g. 'font13')
        :param textColor: hexstring - color of enabled radio button's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: hexstring - color of disabled radio button's label. (e.g. '0xFFFF3300')
        :param shadowColor: hexstring - color of radio button's label's shadow. (e.g. '0xFF000000')
        :param focusedColor: hexstring - color of focused radio button's label. (e.g. '0xFFFFFF00')

        Example::

            self.radiobutton.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')
        """
        pass

    def setRadioDimension(self, x, y, width, height):
        """Sets the radio buttons's radio texture's position and size.

        :param x: integer - x coordinate of radio texture.
        :param y: integer - y coordinate of radio texture.
        :param width: integer - width of radio texture.
        :param height: integer - height of radio texture.

        Example::

            radiobutton.setRadioDimension(x=100, y=5, width=20, height=20)
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class ControlSpin(Control):
    """
    ControlSpin class.

    .. warning:: Not working yet.

    you can't create this object, it is returned by objects likeControlTextBox andControlList.
    """

    def setTextures(self, up, down, upFocus, downFocus):
        """
        setTextures(up, down, upFocus, downFocus)--Set's textures for this control.

        texture are image files that are used for example in the skin
        """
        pass


# noinspection PyUnusedLocal, PyMethodMayBeStatic
class Action(object):
    """Action class.

    For backwards compatibility reasons the == operator is extended so that it
    can compare an action with other actions and action.GetID() with numbers.

    Example::

        if action == ACTION_MOVE_LEFT:
            do.something()
    """

    def getId(self):
        """Returns the action's current id as a long or 0 if no action is mapped in the xml's."""
        return _support.long_type()

    def getButtonCode(self):
        """Returns the button code for this action."""
        return _support.long_type()

    def getAmount1(self):
        """Returns the first amount of force applied to the thumbstick."""
        return float()

    def getAmount2(self):
        """Returns the second amount of force applied to the thumbstick."""
        return float()


def getCurrentWindowId():
    """
    Returns the id for the current 'active' window as an integer.

    example::

        wid = xbmcgui.getCurrentWindowId()
    """
    return _support.long_type()


def getCurrentWindowDialogId():
    """
    Returns the id for the current 'active' dialog as an integer.

    example::

        wid = xbmcgui.getCurrentWindowDialogId()
    """
    return _support.long_type()
