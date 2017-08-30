# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library Imports
from collections import MutableMapping
from time import strptime, strftime
import logging
import os
import re

# Kodi imports
import xbmcplugin
import xbmcgui

# Package imports
from codequick.base import Script
from codequick.support import auto_sort, build_path, logger_id, dispatcher
from codequick.utils import safe_path, ensure_unicode, ensure_native_str, unicode_type, long_type

# Logger specific to this module
logger = logging.getLogger("%s.listitem" % logger_id)

# Listitem thumbnail locations
local_image = ensure_native_str(os.path.join(Script.get_info("path"), u"resources", u"media", u"{}"))
global_image = ensure_native_str(os.path.join(Script.get_info("path_global"), u"resources", u"media", u"{}"))

# Prefetch fanart/icon for use later
_fanart = Script.get_info("fanart")
fanart = ensure_native_str(_fanart) if os.path.exists(safe_path(_fanart)) else None
icon = ensure_native_str(Script.get_info("icon"))

# Stream type map to ensure proper stream value types
stream_type_map = {"duration": int,
                   "channels": int,
                   "aspect": float,
                   "height": int,
                   "width": int}

# Listing sort methods & sort mappings.
# Skips infolables that have no sortmethod and type is string. As by default they will be string anyway
infolable_map = {"artist": (None, xbmcplugin.SORT_METHOD_ARTIST_IGNORE_THE),
                 "studio": (ensure_native_str, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE),
                 "title": (ensure_native_str, xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE),
                 "album": (ensure_native_str, xbmcplugin.SORT_METHOD_ALBUM_IGNORE_THE),
                 "code": (ensure_native_str, xbmcplugin.SORT_METHOD_PRODUCTIONCODE),
                 "count": (int, xbmcplugin.SORT_METHOD_PROGRAM_COUNT),
                 "rating": (float, xbmcplugin.SORT_METHOD_VIDEO_RATING),
                 "mpaa": (ensure_native_str, xbmcplugin.SORT_METHOD_MPAA_RATING),
                 "year": (int, xbmcplugin.SORT_METHOD_VIDEO_YEAR),
                 "listeners": (int, xbmcplugin.SORT_METHOD_LISTENERS),
                 "tracknumber": (int, xbmcplugin.SORT_METHOD_TRACKNUM),
                 "episode": (int, xbmcplugin.SORT_METHOD_EPISODE),
                 "country": (ensure_native_str, xbmcplugin.SORT_METHOD_COUNTRY),
                 "genre": (None, xbmcplugin.SORT_METHOD_GENRE),
                 "date": (ensure_native_str, xbmcplugin.SORT_METHOD_DATE),
                 "size": (long_type, xbmcplugin.SORT_METHOD_SIZE),
                 "sortepisode": (int, None),
                 "sortseason": (int, None),
                 "userrating": (int, None),
                 "discnumber": (int, None),
                 "playcount": (int, None),
                 "overlay": (int, None),
                 "season": (int, None),
                 "top250": (int, None),
                 "setid": (int, None),
                 "dbid": (int, None)}

# Convenient function for adding to autosort set
auto_sort_add = auto_sort.add

# Map quality values to it's related video resolution, used by 'strea.hd'
quality_map = ((768, 576), (1280, 720), (1920, 1080), (3840, 2160))  # SD, 720p, 1080p, 4K

# Re.sub to remove formatting from label strings
strip_formatting = re.compile("\[[^\]]+?\]").sub

# Localized string Constants
YOUTUBE_CHANNEL = 32001
RELATED_VIDEOS = 32201
RECENT_VIDEOS = 32002
ALLVIDEOS = 32003
NEXT_PAGE = 33078
SEARCH = 137


class CommonDict(MutableMapping):
    def __init__(self):
        self.raw_dict = {}

    def __getitem__(self, key):
        """
        Return the item from dictionary with given key. Raises a KeyError if key is not in the map.

        .. note:: All string values will be converted to unicode when returned.

        :param str key: The key required for requested value.
        :return: The saved value.
        :raise KeyError: If key is not in the dictionary.
        """
        value = self.raw_dict[key]
        return value.decode("utf8") if isinstance(value, bytes) else value

    def __setitem__(self, key, value):
        """
        Add a value to dictionary with given key.

        :param str key: The name to set.
        :param value: The value to add to key.
        """
        self.raw_dict[key] = value

    def __delitem__(self, key):
        """
        Remove key from dictionary.

        :param str key: The key to remove from dictionary.
        :raises KeyError: If key is not in the dictionary.
        """
        del self.raw_dict[key]

    def __contains__(self, key):
        return key in self.raw_dict

    def __len__(self):
        return len(self.raw_dict)

    def __iter__(self):
        return iter(self.raw_dict)

    def __str__(self):
        return str(self.raw_dict)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.raw_dict)


class Art(CommonDict):
    def __init__(self, listitem):
        super(Art, self).__init__()
        self._listitem = listitem

    def __setitem__(self, key, value):
        """
        Custom setter that converts unicode values to 'utf8' encoded strings.

        :param str key: The art name to set e.g. thumb, icon or fanart.
        :param value: The path to the image.
        :type value: str or unicode
        """
        if value:
            self.raw_dict[key] = ensure_native_str(value)
        else:
            logger.debug("Ignoring empty art value: '%s'", key)

    def local_thumb(self, image):
        """
        Set the thumbnail image to a image file located in the add-on 'resources/media' directory.
        
        :param image: Filename of the image.
        :type image: str or unicode
        """
        # Here we can't be sure if 'image' only contains ascii characters
        # So ensure_native_str is needed
        self.raw_dict["thumb"] = local_image.format(ensure_native_str(image))

    def global_thumb(self, image):
        """
        Set the thumbnail image to a image file located in the codequick 'resources/media' directory.
        
        Below is a list of available global thumbnail images::

            next.png        - Arrow pointing to the right.
            videos.png      - Circle with a play button in the middle.
            search.png      - An image of a magnifying glass.
            search_new.png  - A magnifying glass with plus symbol in the middle.
            playlist.png    - Image of three bulleted lines.
            recent.png      - Image of a clock.

        :param image: Filename of the image.
        :type image: str or unicode
        """
        # Here we know that 'image' should only contain ascii characters
        # So there is no neeed to use ensure_native_str
        self.raw_dict["thumb"] = global_image.format(image)

    def _close(self):
        if fanart and "fanart" not in self.raw_dict:
            self.raw_dict["fanart"] = fanart
        if "thumb" not in self.raw_dict:
            self.raw_dict["thumb"] = icon
        self._listitem.setArt(self.raw_dict)


class Info(CommonDict):
    def __init__(self, listitem, ctype):
        super(Info, self).__init__()
        self._listitem = listitem
        self._ctype = ctype

    def __setitem__(self, key, value):
        """
        Custom setter that converts values to required type, if known.
        Also converts unicode values to 'utf8' encoded strings.
        
        :param str key: The infolabel name to set e.g. duration, genre or size.
        :param value: The infolabel value.
        """
        if value is None or value == "":
            logger.debug("Ignoring empty infolable: '%s'", key)
            return None

        # Convert duration into an integer
        elif key == "duration":
            auto_sort_add(xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
            self.raw_dict[key] = self._duration(value)
        else:
            # The sort method to set and the type that the infolabel should be
            type_converter, sort_type = infolable_map.get(key, (None, None))

            # Convert value to required type needed for this infolabel
            if type_converter:
                try:
                    value = type_converter(value)
                except ValueError:
                    msg = "value of '%s' for infolabel '%s', is not of type '%s'"
                    raise TypeError(msg % (value, key, type_converter))
                else:
                    self.raw_dict[key] = value

            elif isinstance(value, str):
                self.raw_dict[key] = value
            elif isinstance(value, unicode_type):
                # Only executes on python 2
                self.raw_dict[key] = value.encode("utf8")
            elif isinstance(value, bytes):
                # Only executes on python 3
                self.raw_dict[key] = value.decode("utf8")
            else:
                self.raw_dict[key] = value

            if sort_type:
                # Set the associated sort method for this infolabel
                auto_sort_add(sort_type)

    def date(self, date, date_format):
        """
        Set the date of the infolabel.
        
        :param date: The date of the inforlabel item.
        :type date: str or unicode
        :param str date_format: The format of the date as a strftime directive e.g. 'june 27, 2017' => '%B %d, %Y'
        
        The List of date formats, can be found here.
        https://docs.python.org/2/library/time.html#time.strftime
        """
        converted_date = strptime(ensure_native_str(date), date_format)
        self.raw_dict["date"] = strftime("%d.%m.%Y", converted_date)  # 01.01.2017
        self.raw_dict["aired"] = strftime("%Y-%m-%d", converted_date)  # 2017-01-01
        self.raw_dict["year"] = strftime("%Y", converted_date)  # 2017
        auto_sort_add(xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        auto_sort_add(xbmcplugin.SORT_METHOD_DATE)

    @staticmethod
    def _duration(duration):
        """
        Converts duration from a string of 'hh:mm:ss' into seconds.

        :param duration: The duration of stream.
        :type duration: int or str or unicode
        :returns: The duration converted to seconds.
        :rtype: int
        """
        if isinstance(duration, (str, unicode_type)):
            if ":" in duration or ";" in duration:
                # Split Time By Marker and Convert to Integer
                time_parts = duration.replace(";", ":").split(":")
                time_parts.reverse()
                duration = 0
                counter = 1

                # Multiply Each 'Time Delta' Segment by it's Seconds Equivalent
                for part in time_parts:
                    duration += int(part) * counter
                    counter *= 60
            else:
                # Convert to Interger
                duration = int(duration)

        return duration

    def _close(self):
        self._listitem.setInfo(self._ctype, self.raw_dict)


class Property(CommonDict):
    def __init__(self, listitem):
        super(Property, self).__init__()
        self._listitem = listitem

    def __setitem__(self, key, value):
        """
        Add listitem property.

        :param str key: The name of the property.
        :param value: The property value.
        :type value: str or unicode
        """
        if value:
            self.raw_dict[key] = ensure_unicode(value)
        else:
            logger.debug("Ignoring empty property: '%s'", key)

    def _close(self):
        for key, value in self.raw_dict:
            self._listitem.setProperty(key, value)


class Stream(CommonDict):
    def __init__(self, listitem):
        super(Stream, self).__init__()
        self._listitem = listitem

    def __setitem__(self, key, value):
        """
        Custom setter that converts unicode values to 'utf8' encoded strings.

        :param str key: The key of the stream detail.
        :param value: The value of the stream detail.
        :type value: str or unicode
        """
        if value is None:
            logger.debug("Ignoring empty stream detail value for: '%s'", key)
            return None

        # Ensure that value is of required type
        type_converter = stream_type_map.get(key, ensure_native_str)
        try:
            value = type_converter(value)
        except ValueError:
            msg = "Value of '%s' for stream info '%s', is not of type '%s'"
            raise TypeError(msg % (value, key, type_converter))
        else:
            self.raw_dict[key] = value

    def hd(self, quality, aspect=None):
        """
        Convenient method to set required stream info to show SD/HD/4K logos.

        The values witch are set are width, height and aspect.
        When no aspect ratio is given, then a ratio of '1.78'(16:9) is set when the quality is greater than SD.

        :type quality: bool or int
        :param quality: Quality of the stream e.g. 0=480p, 1=720p, 2=1080p, 3=4K.
        :param float aspect: [opt] The aspect ratio of the video.
        """
        # Skip if value is None(Unknown), useful when passing a variable with unkown value
        if quality is None:
            return None

        # Set video resolution
        try:
            self.raw_dict["width"], self.raw_dict["height"] = quality_map[quality]
        except IndexError:
            raise ValueError("quality id must be within range (0 to 3): '{}'".format(quality))

        # Set the aspect ratio if one is given
        if aspect:
            self["aspect"] = aspect

        # Or set the aspect ratio to 16:9 for HD content and above
        elif self.raw_dict["height"] >= 720:
            self.raw_dict["aspect"] = 1.78

    def _close(self):
        video = {}
        subtitle = {}
        audio = {"channels": 2}
        # Populate the above dictionary with the appropriate key/value pairs
        for key, value in self.raw_dict.items():
            rkey = key.split("_")[-1]
            if key in ("video_codec", "aspect", "width", "height", "duration"):
                video[rkey] = value
            elif key in ("audio_codec", "audio_language", "channels"):
                audio[rkey] = value
            elif key == "subtitle_language":
                subtitle[rkey] = value
            else:
                raise KeyError("unknown stream detail key: '{}'".format(key))

        # Now we are ready to send the stream info to kodi
        if audio:
            self._listitem.addStreamInfo("audio", audio)
        if video:
            self._listitem.addStreamInfo("video", video)
        if subtitle:
            self._listitem.addStreamInfo("subtitle", subtitle)


class Context(list):
    def __init__(self, listitem):
        super(Context, self).__init__()
        self._listitem = listitem

    def related(self, callback, **query):
        """
        Convenient method to add a related videos context menu container item.

        Keyword arguments can be any json serializable object e.g. str, list, dict.
        
        :param callback: The function that will be called when menu item is activated.
        :param query: [opt] Keyword arguments that will be passed on to callback function.
        """
        self.container(Script.localize(RELATED_VIDEOS), callback, **query)

    def container(self, label, callback, **query):
        """
        Convenient method to add a context menu container item.

        Keyword arguments can be any json serializable object e.g. str, list, dict.
        
        :param label: The label of the context menu item.
        :param callback: The function that will be called when menu item is activated.
        :param query: [opt] Keyword arguments that will be passed on to callback function.
        """
        command = "XBMC.Container.Update(%s)" % build_path(callback.route.path, query)
        self.append((label, command))

    def _close(self):
        if self:
            self._listitem.addContextMenuItems(self)


class Listitem(object):
    """
    The list item control is used for creating item lists in Kodi.

    :param str ctype: Type of content been listed. e.g. video, music, pictures or game.

    Usage::

        for elem in root_elem.iterfind("li"):
            a_tag = elem.find("a")

            # Create new listitem object
            item = ListItem()

            # Set label of listitem
            item.set_label(a_tag.text)

            # Set thumbnail image
            item.art["thumb"] = elem.find("img").get("src")

            # Set callback function with arguments
            item.set_callback(some_callback_func, cat=a_tag.get("href"))

            # Return the listitem object
            yield item
    """

    def __init__(self, ctype="video"):
        self._path = ""

        self.listitem = listitem = xbmcgui.ListItem()
        """The underlining kodi listitem object, for advanced use."""

        self.params = CommonDict()
        """
        Dictionary like object for parameters that will be passed to the callback object.
        
        Parameters can be any json serializable object e.g. str, list, dict.
        
        Example::
        
            item.params['videoid'] = 'kqmdIV_gBfo'
        """

        self.info = Info(listitem, ctype)
        """
        :class:`Info` object for adding infoLabels:
        
        This is a dictionary like object that allows you to add listitem infoLabels. e.g. duration, genre, size.
        
        Sort methods will be automaticly selected and the object type will
        be converted to what is required for each infolabel.
        
        'duration' will be converted to integer and sort method will be set to 'SORT_METHOD_VIDEO_RUNTIME'.
        'size' will be converted to long and sort method will be set to 'SORT_METHOD_SIZE'.

        .. note:: Duration infolabel value, can be either in seconds or as a 'hh:mm:ss' string.
        .. note:: Any unicode values will be converted to 'UTF-8' encoded strings.

        The full list of listitem infoLabels, can be found at.
        https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        
        Examples::
        
            item.info['genre'] = 'Science Fiction'
            item.info['size'] = 256816
            item.info.date('june 27, 2017', '%B %d, %Y'))
        """

        self.art = Art(listitem)
        """
        :class:`Art` object for adding listitem's art.

        This is a dictionary like object that allows you to add various image values. e.g. thumb, fanart.

        The full list of art values, can be found here.
        https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#gad3f9b9befa5f3d2f4683f9957264dbbe

        Usage::
        
            item.art['thumb"] = 'http://www.example.ie/image.jpg'
            item.art['fanart"] = 'http://www.example.ie/fanart.jpg'
            item.art.local_thumb('local_art.png')
        """

        self.stream = Stream(listitem)
        """
        :class:`Stream` object for adding stream details.

        This is a dictionary like object that allows you to add stream details. e.g. video_codec, audio_codec.
        
        Stream Values::
        
            video_codec        : string (h264)
            aspect             : float (1.78)
            width              : integer (1280)
            height             : integer (720)
            channels           : integer (2)
            audio_codec        : string (AAC)
            audio_language     : string (en)
            subtitle_language  : string (en)
        
        Example::
        
            item.stream['video_codec'] = 'h264'
            item.stream['audio_codec'] = 'aac'
            item.stream.hd(2, aspect=1.78) # 1080p
        """

        self.property = Property(listitem)
        """
        :class:`Property` object for adding listitem properties.

        This is a dictionary like object that allows you to add listitem properties. e.g. StartOffset
        
        Some of these are treated internally by Kodi, such as the 'StartOffset' property,
        which is the offset in seconds at which to start playback of an item. Others may be used
        in the skin to add extra information, such as 'WatchedCount' for tvshow items.

        Examples::
        
            item.property['StartOffset'] = '256.4'
        """

        self.context = Context(listitem)
        """
        :class:`list` object for context menu items.

        This is a list containing tuples, consisting of label/function pairs.
        
        label: str or unicode - item's label.
        function: str or unicode - any built-in function to perform e.g. XBMC.Container.Update

        The full list of built-in functions can be found here.
        http://kodi.wiki/view/List_of_Built_In_Functions
        """

    @property
    def label(self):
        """The listitem label."""
        return ensure_unicode(self.listitem.getLabel())

    @label.setter
    def label(self, label):
        """
        Sets the listitem's label.

        Refor to: 'http://kodi.wiki/view/Label_Formatting' for full label formating options.

        :param label: The label of the listitem.
        :type label: str or unicode
        """
        self.listitem.setLabel(label)
        unformatted_label = strip_formatting("", label)
        self.params["_title_"] = unformatted_label
        self.info["title"] = unformatted_label

    def set_callback(self, callback, *args, **kwargs):
        """
        Sets the callback function or playable path.

        Arguments can be any json serializable object e.g. str, list, dict.
        
        :param callback: The function to callback or a playable path to a video.
        :type callback: :class:`types.FunctionType` or :class:`codequick.Base` or str or unicode
        :param args: Positional arguments that will be passed to callback.
        :param kwargs: Keyword arguments that will be passed to callback.
        """
        if args:
            # Convert positional arguments to keyword arguments
            args_map = callback.route.args_to_kwargs(args)
            kwargs.update(args_map)

        self._path = callback
        self.params.update(kwargs)

    # noinspection PyProtectedMember
    def _close(self):
        callback = self._path
        if hasattr(callback, "route"):
            self.listitem.setProperty("isplayable", str(callback.route.is_playable).lower())
            self.listitem.setProperty("folder", str(callback.route.is_folder).lower())
            path = build_path(callback.route.path, self.params.raw_dict)
            isfolder = callback.route.is_folder
        else:
            self.listitem.setProperty("isplayable", "true" if callback else "false")
            self.listitem.setProperty("folder", "false")
            path = callback
            isfolder = False

        if isfolder:
            # Set Kodi icon image if not already set
            if "icon" not in self.art.raw_dict:
                self.art.raw_dict["icon"] = "DefaultFolder.png"
        else:
            # Set Kodi icon image if not already set
            if "icon" not in self.art.raw_dict:
                self.art.raw_dict["icon"] = "DefaultVideo.png"

            # Add Video Specific Context menu items
            self.context.append(("$LOCALIZE[13347]", "XBMC.Action(Queue)"))
            self.context.append(("$LOCALIZE[13350]", "XBMC.ActivateWindow(videoplaylist)"))

            # Close video related datasets
            self.stream._close()

        # Add label as plot if no plot is found
        if "plot" not in self.info:
            self.info["plot"] = self.label

        # Close common datasets
        self.listitem.setPath(path)
        self.property._close()
        self.context._close()
        self.info._close()
        self.art._close()

        # Return a tuple compatible with 'xbmcplugin.addDirectoryItems'
        return path, self.listitem, isfolder

    @classmethod
    def from_dict(cls, label, callback, params=None, info=None, art=None, stream=None, properties=None, context=None):
        """
        Constructor to create a listitem.

        This method will create and populate a listitem from a set of listitem values.

        :type label: str or unicode
        :param label: The listitem's label.
        :param callback: The callback function or playable path.
        :param dict params: Dictionary of parameters that will be passed to the callback function.
        :param dict info: Dictionary of listitem infoLabels.
        :param dict art: Dictionary of listitem's art.
        :param dict stream: Dictionary of stream details.
        :param dict properties: Dictionary of listitem properties.
        :param list context: List of context menu item(s) containing tuples of label/command pairs.

        :return: A listitem object.
        :rtype: Listitem
        """
        item = cls()
        item.set_callback(callback)
        item.label = label

        if params:
            item.params.update(params)
        if info:
            item.info.update(info)
        if art:
            item.art.update(art)
        if stream:
            item.stream.update(stream)
        if properties:
            item.property.update(properties)
        if context:
            item.context.extend(context)

        return item

    @classmethod
    def next_page(cls, **params):
        """
        A Listitem constructor for adding Next Page listitem.

        :param params: [opt] Keyword arguments of params that will be added to the current set of callback params.
        """
        # Add support params to callback params
        params["_updatelisting_"] = True
        params["_title_"] = Script.params.get(u"_title_", u"")
        params["_nextpagecount_"] = Script.params.get(u"_nextpagecount_", 1) + 1

        # Create listitem instance
        item = cls()
        label = u"%s %i" % (Script.localize(NEXT_PAGE), params["_nextpagecount_"])
        item.info["plot"] = "Show the next page of content."
        item.label = "[B]%s[/B]" % label
        item.art.global_thumb("next.png")
        item.params.update(params)
        item.set_callback(dispatcher.callback, **params)
        return item

    @classmethod
    def recent(cls, callback, **params):
        """
        A Listitem constructor for adding Recent Folder listitem.

        :param callback: The callback function.
        :type callback: :class:`types.FunctionType`

        :param params: Keyword arguments of parameters that will be passed to the callback function.
        """
        # Create listitem instance
        item = cls()
        item.label = Script.localize(RECENT_VIDEOS)
        item.info["plot"] = "Show the most recent videos."
        item.art.global_thumb("recent.png")
        item.set_callback(callback, **params)
        return item

    @classmethod
    def search(cls, callback, **params):
        """
        A Listitem constructor to add saved search Support to addon.

        :param callback: Function that will be called when the listitem is activated.
        :param params: Keyword arguments that will be farwarded on to callback.

        Example::

            Listitem.search(video_search, "https://www.google.com/?q=%s")
        """
        item = cls()
        item.label = u"[B]%s[/B]" % Script.localize(SEARCH)
        item.art.global_thumb("search.png")
        item.info["plot"] = "Search for video content."
        item.set_callback(SavedSearches, route=callback.route.path, **params)
        return item

    @classmethod
    def youtube(cls, content_id, label=None, enable_playlists=True):
        """
        A Listitem constructor to add a youtube channel to addon.

        :param content_id: Channel name, channel id or playlist id to list videos from.
        :type content_id: str or unicode

        :param label: [opt] Label of listitem. (default => 'All Videos').
        :type label: str or unicode

        :param bool enable_playlists: [opt] Set to True to enable linking to channel playlists. (default => True)
        """
        # Youtube exists, Creating listitem link
        item = cls()
        item.label = label if label else Script.localize(ALLVIDEOS)
        item.art.global_thumb("videos.png")
        item.params["contentid"] = content_id
        item.params["enable_playlists"] = False if content_id.startswith("PL") else enable_playlists
        item.set_callback(YTPlaylist)
        return item


# Import callback functions required for listitem constructs
from codequick.youtube import Playlist as YTPlaylist
from codequick.search import SavedSearches
