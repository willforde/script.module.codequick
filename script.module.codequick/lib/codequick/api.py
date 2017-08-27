# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library Imports
import logging
import inspect
import re

# Kodi imports
import xbmcplugin
import xbmcgui
import xbmc

# Package imports
from codequick.base import dispatcher, Script, build_path, logger_id
from codequick.utils import unicode_type, ensure_native_str, ensure_unicode

# Logger specific to this module
logger = logging.getLogger("%s.api" % logger_id)

# Convenience function to call dispatcher
run = dispatcher.dispatch

# Localized string Constants
SELECT_PLAYBACK_ITEM = 25006
NO_DATA = 33077


class Route(Script):
    """
    This class is used to create Route callbacks. Route callbacks, are callbacks that
    return listitems witch are expected to be listed in kodi.

    Route inherits all methods and attributes from :class:`Script`.
    """

    # Change listitem type to 'folder'
    is_folder = True

    def __init__(self):
        super(Route, self).__init__()
        self._manual_sort = set()

        self.autosort = True
        """bool: False value will disable autosort."""

        self.update_listing = self.params.get(u"_updatelisting_", False)
        """bool: True, this folder should update the current listing. False, this folder is a subfolder (default)."""

        self.content_type = None
        """
        str: The plugins content type. If not given it will default to files/videos based on type of content.
        
        'files' when listing folders.
        'videos' when listing videos.
        """

    def _execute_route(self, callback):
        """Execute the callback function and process the results."""

        # Fetch all listitems from callback function
        listitems = super(Route, self)._execute_route(callback)

        # Process listitems and close
        success = self.__add_listitems(listitems)
        self.__end_directory(success)

    def __add_listitems(self, raw_listitems):
        """Handle the processing of the listitems."""
        # Convert listitem to list incase we have a generator
        if inspect.isgenerator(raw_listitems):
            raw_listitems = list(raw_listitems)

        # Check if raw_listitems is None or an empty list
        if not raw_listitems:
            raise RuntimeError("No items found")

        # Create a new list containing tuples, consisting of path, listitem, isfolder.
        listitems = []
        folder_counter = 0.0
        for listitem in raw_listitems:
            if listitem:
                # noinspection PyProtectedMember
                listitem_tuple = listitem._close()
                listitems.append(listitem_tuple)
                if listitem_tuple[2]:
                    folder_counter += 1

        # Guess if this directory listing is primarily a folder or video listing.
        # Listings will be considered to be a folder if more that half the listitems are folder items.
        isfolder = folder_counter > (len(listitems) / 2)
        self.__content_type(isfolder)

        # Pass the listitems and relevant data to kodi
        return xbmcplugin.addDirectoryItems(self.handle, listitems, len(listitems))

    def __content_type(self, isfolder):
        """Configure plugin properties, content, category and sort methods."""

        # Set the add-on content type
        xbmcplugin.setContent(self.handle, "files" if isfolder else "videos")

        # Sets the category for skins to display modes.
        xbmcplugin.setPluginCategory(self.handle, ensure_native_str(re.sub(u"\(\d+\)$", u"", self._title).strip()))

        # Add sort methods only if not a folder(Video listing)
        if not isfolder:
            self.__add_sort_methods(self._manual_sort)

    def __add_sort_methods(self, manual):
        """Add sort methods to kodi."""
        if self.autosort:
            manual.update(auto_sort)

        if manual:
            # Sort the list of sort methods before adding to kodi
            _addSortMethod = xbmcplugin.addSortMethod
            for sortMethod in sorted(manual):
                _addSortMethod(self.handle, sortMethod)
        else:
            # If no sortmethods are given then set sort mehtod to unsorted
            xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_UNSORTED)

    def __end_directory(self, success):
        """Mark the end of directory listings."""
        xbmcplugin.endOfDirectory(self.handle, success, self.update_listing, False)

    def add_sort_methods(self, *methods, **override):
        """
        Adds sorting method(s) for the media list.

        Any number of sort methods can be given as multiple arguments.
        Normally this should not be needed as sort methods are auto detected.

        :param int methods: One or more kodi sort mehtods.
        :param bool override: [opt] keyword argument to override the auto selected sort methods. (default => False)

        .. Example::

            plugin.add_sort_methods(xbmc.SORT_METHOD_DATE, xbmc.SORT_METHOD_DURATION, override=True)
        """
        # Disable auto sort if override is True, Default
        self.autosort = self.autosort and not override.get("override", False)
        self._manual_sort.update(methods)


class Resolver(Script):
    """
    This class is used to create Resolver callbacks. Resolver callbacks, are callbacks that
    return playable video urls witch kodi can play.

    Resolver inherits all methods and attributes from :class:`Script`.

    The expected return types from the callback resolver::

        * bytes: Url as type bytes.
        * unicode: Url as type unicode.
        * iterable: List or tuple, consisting of url's, listItem's or tuple's consisting of title and url.
        * dict: Dictionary consisting of title as the key and the url as the value.
        * listItem: A kodi listitem object with required data already set e.g. label and path.

    When multiple url's are given, a playlist will be automaticly created.
    """
    # Change listitem type to 'player'
    is_playable = True

    def _execute_route(self, callback):
        """Execute the callback function and process the results."""
        resolved = super(Resolver, self)._execute_route(callback)
        self.__send_to_kodi(resolved)

    def create_loopback(self, url, **next_params):
        """
        Create a playlist where the second item loops back to current addon to load next video.

        Useful for faster playlist resolving by only resolving the video url as the playlist progresses.
        No need to resolve all video urls at once before playing the playlist.

        Also useful for continuous playback of videos with no foreseeable end. For example, party mode.

        :param url: Url for the first playable listitem.
        :type url: str or unicode

        :param next_params: [opt] Keyword arguments to add to the loopback request when accessing the next video.

        :returns: The Listitem that kodi will play
        :rtype: xbmcgui.ListItem

        .. Example::

            plugin.create_loopback("http://example.com/a5ed59gk.mkv", video_set=["kd90k3lx", "j5yj9y7p", "1djy6k7e"])
        """
        # Video Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

        # Main Playable listitem
        main_listitem = xbmcgui.ListItem()
        main_listitem.setPath(url)

        # When called from a loopback we just add title to main listitem
        if self._title.startswith(u"_loopback_"):
            main_listitem.setLabel(self._title.split(u" - ", 1)[1])
            next_params["_title_"] = self._title
        else:
            # Create playlist for loopback calling
            # The first item is the playable listitem
            main_listitem.setLabel(self._title)
            next_params["_title_"] = u"_loopback_ - %s" % self._title
            playlist.clear()
            playlist.add(url, main_listitem)

        # Create Loopback listitem
        loop_listitem = xbmcgui.ListItem()
        loop_listitem.setLabel(next_params["_title_"])

        # Build a loopback url that callback to the addon to fetch the next video
        loopback_url = build_path(**next_params)
        loop_listitem.setPath(loopback_url)
        playlist.add(loopback_url, loop_listitem)

        # Retrun the playable listitem
        return main_listitem

    def extract_source(self, url, quality=None):
        """
        Extract video url using YoutubeDL.

        The YoutubeDL module provides access to youtube-dl video stream extractor
        witch gives access to hundreds of sites.

        Quality is 0=SD, 1=720p, 2=1080p, 3=Highest Available

        .. seealso:: https://rg3.github.io/youtube-dl/supportedsites.html

        :param url: Url to fetch video for.
        :type url: str or unicode
        :param int quality: [opt] Override youtubeDL's quality setting.

        :returns: The extracted video url
        :rtype: str

        ..note::

            Unfortunately the kodi YoutubeDL module is python2 only.
            Hopefully it will be ported to python3 when kodi gets upgraded.
        """
        def ytdl_logger(record):
            if record.startswith("ERROR:"):
                # Save error rocord for raising later, outside of the callback
                # YoutubeDL ignores errors inside callbacks
                stored_errors.append(record[7:])

            self.log(record)
            return True

        # Setup YoutubeDL module
        from YDStreamExtractor import getVideoInfo, setOutputCallback
        setOutputCallback(ytdl_logger)
        stored_errors = []

        # Atempt to extract video source
        video_info = getVideoInfo(url, quality)
        if video_info:
            if video_info.hasMultipleStreams():
                # More than one stream found, Ask the user to select a stream
                return self.__source_selection(video_info)
            else:
                return video_info.streamURL()

        # Raise any stored errors
        elif stored_errors:
            raise RuntimeError(stored_errors[0])

    def __source_selection(self, video_info):
        """
        Ask user with video stream to play.

        :param video_info: YDStreamExtractor video_info object.
        :returns: Stream url of video
        :rtype: str
        """
        display_list = []
        # Populate list with name of extractor ('YouTube') and video title.
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
                          List may consist of url or listitem object.

        :returns The first listitem of the playlist.
        :rtype: xbmcgui.ListItem
        """
        # Create Playlist
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        title = self._title

        # Loop each item to create playlist
        for count, url in enumerate(filter(None, urls), 1):
            # Kodi original listitem object
            if isinstance(url, xbmcgui.ListItem):
                listitem = url
            # Custom listitem object
            elif isinstance(url, Listitem):
                # noinspection PyProtectedMember
                listitem = url._close()[1]
            else:
                # Not already a listitem object
                listitem = xbmcgui.ListItem()
                if isinstance(url, (list, tuple)):
                    title, url = url
                    title = ensure_unicode(title)

                # Create listitem with new title
                listitem.setLabel(u"%s Part %i" % (title, count))
                listitem.setPath(url)

            # Populate Playlis
            playlist.add(listitem.getPath(), listitem)

        # Return the first playlist item
        return playlist[0]

    def __send_to_kodi(self, resolved):
        """
        Construct playable listitem and send to kodi.

        :param resolved: The resolved url to send back to kodi.
        :type resolved: str or unicode or :class:`xbmcgui.ListItem` or :class:`codequick.Listitem`.
        """

        # Create listitem object if resolved object is a string or unicode
        if isinstance(resolved, (bytes, unicode_type)):
            listitem = xbmcgui.ListItem()
            listitem.setPath(resolved)

        # Create playlist if resolved object is a list of urls
        elif isinstance(resolved, (list, tuple)) or inspect.isgenerator(resolved):
            listitem = self.__create_playlist(resolved)

        # Create playlist if resolved is a dict of {title: url}
        elif hasattr(resolved, "items"):
            listitem = self.__create_playlist(resolved.items())

        # Directly use resoleved if its already a listitem
        elif isinstance(resolved, xbmcgui.ListItem):
            listitem = resolved

        # Extract original kodi listitem from custom listitem
        elif isinstance(resolved, Listitem):
            # noinspection PyProtectedMember
            listitem = resolved._close()[1]

        # Invalid or No url was found
        elif resolved:
            raise ValueError("resolver returned invalid url of type: '%s'" % type(resolved))
        else:
            raise ValueError(self.localize(NO_DATA))

        # Send playable listitem to kodi
        xbmcplugin.setResolvedUrl(self.handle, True, listitem)


# Now we can import the listing module
from .listing import Listitem, auto_sort
