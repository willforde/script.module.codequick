# -*- coding: utf-8 -*-

# Standard Library Imports
from functools import partial
import logging
import re

# Kodi imports
import xbmcplugin
import xbmcgui
import xbmc

# Package imports
from .support import Dispatcher, Script, build_path, handle, logger_id
from .listing import Listitem, auto_sort

# Logger specific to this module
logger = logging.getLogger("%s.api" % logger_id)

# Dispatcher to manage route callbacks
dispatcher = Dispatcher()

# Localized string Constants
SELECT_PLAYBACK_ITEM = 25006
YOUTUBE_CHANNEL = 32901
MOST_RECENT = 32902
NEXT_PAGE = 33078
SEARCH = 137


class Route(Script):
    """Add Directory List Items to Kodi"""

    # Change listitem type to 'folder'
    is_folder = True

    def __init__(self):
        super(Route, self).__init__()
        self._nextpagecount = self.params.pop("_nextpagecount_", 1)
        self._manual_sort = set()
        self._autosort = True

        self.update_listing = self.params.pop("_updatelisting_", False)
        """bool: True, this folder should update the current listing. False, this folder is a subfolder(Default)."""

    def execute_route(self, callback):
        """Execute the callback function and process the results."""

        # Fetch all listitems from callback function
        listitems = super(Route, self).execute_route(callback)

        # Process listitems and close
        self.__add_listitems(listitems)
        self.__add_sort_methods(self._manual_sort)
        self.__end_directory(True)

    def __add_listitems(self, raw_listitems):
        if not raw_listitems:
            raise RuntimeError("No listitems found")

        # Create a new list containing tuples, consisting of path, listitem, isfolder.
        listitems = []
        folder_counter = 0
        for listitem in raw_listitems:
            if listitem:
                listitem_tuple = listitem.close()
                listitems.append(listitem_tuple)
                if listitem_tuple[2]:
                    folder_counter += 1

        # Pass the listitems and relevant data to kodi
        xbmcplugin.addDirectoryItems(handle, listitems, len(listitems))

        # Guess if this directory listing is primarily a folder or a video listing.
        # Listings will be considered to be a folder if more that half the listitems are folder items.
        isfolder = folder_counter > (len(listitems) / 2)
        self.__content_type(isfolder)

    def __content_type(self, isfolder):
        """Guess content type and set kodi parameters, setContent & SetViewMode"""

        # Set the add-on content type
        xbmcplugin.setContent(handle, "albums")

        # Sets the category for skins to display modes.
        xbmcplugin.setPluginCategory(handle, re.sub("\(\d+\)$", "", self._title).strip())

        # Change preferred view mode if one was set for given content type
        set_key = "{}.{}.view".format(xbmc.getSkinDir(), "folder" if isfolder else "video")
        view_mode = self.setting[set_key]
        if view_mode:
            xbmc.executebuiltin("Container.SetViewMode({})".format(view_mode))

    def __add_sort_methods(self, manual):
        """Add sort methods to kodi"""
        if self._autosort:
            manual.update(auto_sort)

        if manual:
            # Sort the list of sort methods before adding to kodi
            _addSortMethod = xbmcplugin.addSortMethod
            for sortMethod in sorted(manual):
                _addSortMethod(handle, sortMethod)
        else:
            # If no sortmethods are given then set sort mehtod to unsorted
            xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)

    def __end_directory(self, success):
        """Mark the end of directory listings."""
        xbmcplugin.endOfDirectory(handle, success, self.update_listing, False)

    def add_sort_methods(self, *methods, **override):
        """
        Adds sorting method(s) for the media list.

        Any number of sort mehtods can be given as multiple arguments.
        Normally this should not be needed as sort methods are auto detected.

        :param int methods: One or more kodi sort mehtods.
        :param bool override: (Optional) keyword argument to override the auto selected sort methods. (Default: False)
        """
        # Disable auto sort if override is True, Default
        self._autosort = self._autosort and not override.get("override", False)
        self._manual_sort.update(methods)

    @staticmethod
    def set_category(category):
        """
        Sets the plugins name for skins to display.

        :param category: Plugins sub category.
        :type category: str, unicode
        
        # Need to test if this function can be more usefull
        """
        xbmcplugin.setPluginCategory(handle, category)

    @staticmethod
    def add_item(callback, label, params=None, info=None, art=None, stream=None, properties=None, context=None):
        """
        Basic constructor to add a simple listitem.

        :param callback: The callback function or playable path.
        :type callback: :class:`types.FunctionType`

        :param label: The listitem's label.
        :type label: str or unicode

        :param dict params: Dictionary of parameters that will be passed to the callback object.
        :param dict info: Dictionary of listitem infoLabels.
        :param dict art: Dictionary of listitem's art.
        :param dict stream: Dictionary of stream details.
        :param dict properties: Dictionary of listitem properties.
        :param list context: List of context menu item(s) containing tuples of label/command pairs.

        :return: A listitem object.
        :rtype: :class:`codequick.Listitem`
        """
        # Create listitem instance
        item = Listitem()
        item.set_callback(callback)
        item.set_label(label)

        # Update listitem data
        if params:
            item.params.update(params)
        if info:
            item.params.update(info)
        if art:
            item.params.update(art)
        if stream:
            item.params.update(stream)
        if properties:
            item.params.update(properties)
        if context:
            item.params.extend(context)

        return item

    def add_next(self, **params):
        """
        A Listitem constructor for adding Next Page item.

        :param params: (Optional) Keyword arguments of params that will be added to the current set of callback params.
        """
        # Fetch current set of callback params and add the extra params if any
        base_params = self.params.copy()
        base_params["_updatelisting_"] = True
        base_params["_nextpagecount_"] = self._nextpagecount + 1
        base_params["_title_"] = self._title

        # Create listitem instance
        item = Listitem()
        label = u"%s %s" % (self.localize(NEXT_PAGE), base_params["_nextpagecount_"])
        item.set_label(label, u"[B]%s[/B]")
        item.art.global_thumb(u"next.png")
        item.params.update(base_params)
        item.set_callback(self, **params)
        return item

    def add_recent(self, callback, **params):
        """
        A Listitem constructor for adding Recent Folder item.

        :param callback: The callback function.
        :type callback: :class:`types.FunctionType`

        :param params: Keyword arguments of parameters that will be passed to the callback function.
        """
        # Create listitem instance
        listitem = Listitem()
        listitem.set_label(self.localize(MOST_RECENT), u"[B]%s[/B]")
        listitem.art.global_thumb(u"recent.png")
        listitem.set_callback(callback, **params)
        return listitem

    def add_search(self, callback, **params):
        """
        A Listitem constructor to add saved search Support to addon.

        :param callback: Function that will be called when the listitem is activated.
        :param params: Dictionary containing url querys to combine with search term.
        """
        listitem = Listitem()
        listitem.set_label(self.localize(SEARCH), u"[B]%s[/B]")
        listitem.art.global_thumb(u"search.png")
        listitem.set_callback(SavedSearches, route=callback.route, **params)
        return listitem

    def add_youtube(self, content_id, label=None, enable_playlists=True, wide_thumb=False):
        """
        A Listitem constructor to add a youtube channel to addon.
        
        :param content_id: Channel name, channel id or playlist id to list videos from.
        :type content_id: str or unicode
        
        :param label: (Optional) Label of listitem. (default: '-Youtube Channel').
        :type label: str or unicode
        
        :param bool enable_playlists: (Optional) Set to True to enable linking to channel playlists. (default => False)
        :param bool wide_thumb: (Optional) True to use a wide thumbnail or False for normal thumbnail image (default).
        """
        # Youtube exists, Creating listitem link
        item = Listitem()
        item.set_label(label if label else self.localize(YOUTUBE_CHANNEL), "[B]%s[/B]")
        item.art.global_thumb(u"youtubewide.png" if wide_thumb else u"youtube.png")
        item.params["contentid"] = content_id
        item.params["enable_playlists"] = enable_playlists
        item.set_callback(YTPlaylist)
        return item


class Resolver(Script):
    # Change listitem type to 'player'
    is_playable = True

    def execute_route(self, callback):
        """Execute the callback function and process the results."""
        resolved = super(Resolver, self).execute_route(callback)
        self.__send_to_kodi(resolved)

    def create_loopback(self, url, **next_params):
        """
        Create a playlist where the second item loops back to current addon to load next video. e.g. Party Mode

        :param url: Url for the first playable listitem.
        :type url: str or unicode

        :param next_params: (Optional) Keyword arguments to add to the loopback request when accessing the next video.

        :returns: The Listitem that kodi will play
        :rtype: :class:`xbmcgui.ListItem`
        """
        # Create Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

        # Create Main listitem
        main_listitem = xbmcgui.ListItem()
        main_listitem.setPath(url)

        if self._title.startswith(u"_loopback_"):
            main_listitem.setLabel(self._title.split(u" - ", 1)[1])
            next_params["title"] = self._title
        else:
            # Add playable listitem as the first playlist item
            main_listitem.setLabel(self._title)
            next_params["title"] = u"_loopback_ - %s" % self._title
            playlist.clear()
            playlist.add(url, main_listitem)

        # Create Loopback listitem
        loop_listitem = xbmcgui.ListItem()
        loop_listitem.setLabel(next_params["title"])

        # Build a loopback url that callback to the addon to fetch the next video
        loopback_url = build_path(**next_params)
        loop_listitem.setPath(loopback_url)
        playlist.add(loopback_url, loop_listitem)

        # Retrun the playable listitem
        return main_listitem

    def extract_source(self, url, quality=None):
        """
        Extract video url using YoutubeDL

        Options for quality parameter:
            0=SD
            1=720p
            2=1080p
            3=4K

        :param url: Url to fetch video for.
        :type url: str or unicode
        :param int quality: (Optional) Override youtubeDL's quality setting.

        :returns: The extracted video url
        :rtype: str
        """
        try:
            # noinspection PyUnresolvedReferences
            from YDStreamExtractor import getVideoInfo, disableDASHVideo
        except ImportError:
            self.log("YoutubeDL module not installed. Please install to enable 'extract_source'", lvl=40)
            raise ImportError("Missing YoutubeDL module")
        else:
            # Disable DASH videos, until youtubeDL supports it
            disableDASHVideo(True)

            # If there is more than one stream found then ask for selection
            video_info = getVideoInfo(url, quality)
            if video_info.hasMultipleStreams():
                # Ask the user to select a stream
                return self.__source_selection(video_info)
            else:
                return video_info.streamURL()

    def __source_selection(self, video_info):
        """
        Ask user with video stream to play

        :param video_info: YDStreamExtractor video_info object
        :returns: Stream url of video
        :rtype: str
        """
        display_list = []
        for stream in video_info.streams():
            data = "%s - %s" % (stream["ytdl_format"]["extractor"].title(), stream["title"])
            display_list.append(data)

        dialog = xbmcgui.Dialog()
        ret = dialog.select(self.localize(SELECT_PLAYBACK_ITEM), display_list)
        if ret >= 0:
            video_info.selectStream(ret)
            return video_info.streamURL()

    def __create_playlist(self, urls):
        """
        Create playlist for kodi and return back the first item of that playlist to play.

        :param list urls: Set of urls that will be used in the creation of the playlist.

        :returns The first listitem of the playlist.
        :rtype: :class:`xbmcgui.ListItem`:
        """
        # Create Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        title = self._title.encode("utf8")

        # Loop each item to create playlist
        for count, url in enumerate(urls, 1):
            listitem = xbmcgui.ListItem()
            if isinstance(url, (list, tuple)):
                url, title = url
                if isinstance(title, unicode):
                    title = title.encode("utf8")

            # Create listitem with new title
            listitem.setLabel("%s Part %i" % (title, count))
            listitem.setPath(url)

            # Populate Playlis
            playlist.add(url, listitem)

        # Return first playlist item to send to kodi
        return playlist[0]

    def __send_to_kodi(self, resolved):
        """ Construct playable listitem and send to kodi

        :param resolved: The resolved url to send back to kodi
        :type resolved: str or unicode or :class:`xbmcgui.ListItem`
        """

        # Create listitem object if resolved object is a string or unicode
        if isinstance(resolved, (str, unicode)):
            listitem = xbmcgui.ListItem()
            listitem.setPath(resolved)

        # Create playlist if resolved a list of urls
        elif isinstance(resolved, (list, tuple)):
            listitem = self.__create_playlist(resolved)

        # Use resoleved as is if its already a listitem
        elif isinstance(resolved, xbmcgui.ListItem):
            listitem = resolved

        # Invalid or No url was found
        elif resolved:
            raise ValueError("resolver returned invalid url: '%s'" % type(resolved))
        else:
            raise ValueError("resolver failed to return url")

        # Send playable listitem to kodi
        xbmcplugin.setResolvedUrl(handle, True, listitem)


def custom_route(path, parent=None):
    """
    Decorator used to register callback functions/classes with custom route path.

    :param str path: The route path for registering callback to.
    :param parent: (Optional) The parent control class, if decorating a function.
    :returns: A preconfigured register decorator.
    """
    return partial(dispatcher.register, cls=parent, custom_route=path)


register_script = partial(dispatcher.register, cls=Script)
register_script.__doc__ = """Decorator used to register 'Script' callback function/class."""

register_route = partial(dispatcher.register, cls=Route)
register_route.__doc__ = """Decorator used to register 'VirtualFS' callback function/class."""

register_resolver = partial(dispatcher.register, cls=Resolver)
register_resolver.__doc__ = """Decorator used to register 'PlayMedia' callback function/class."""

run = dispatcher.dispatch

from .internal import SavedSearches
from youtube import Playlist as YTPlaylist
