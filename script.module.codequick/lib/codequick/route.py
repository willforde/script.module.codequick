# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library Imports
import logging
import inspect
import re

# Kodi imports
import xbmcplugin

# Package imports
from codequick.script import Script
from codequick.support import logger_id, auto_sort
from codequick.utils import ensure_native_str

__all__ = ["Route"]

# Logger specific to this module
logger = logging.getLogger("%s.route" % logger_id)

# Localized string Constants
SELECT_PLAYBACK_ITEM = 25006
NO_DATA = 33077


class Route(Script):
    """
    This class is used to create Route callbacks. Route callbacks, are callbacks that
    return listitems witch show up as folders in kodi.

    Route inherits all methods and attributes from :class:`script.Script<codequick.script.Script>`.
    """

    # Change listitem type to 'folder'
    is_folder = True

    def __init__(self):
        super(Route, self).__init__()
        self.update_listing = self.params.get(u"_updatelisting_", False)
        self._manual_sort = set()
        self.content_type = None
        self.autosort = True

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
        content_type = self.content_type or "files" if isfolder else "videos"
        xbmcplugin.setContent(self.handle, content_type)

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

    def add_sort_methods(self, *methods):
        """
        Adds sorting method(s) for the media list.

        Any number of sort methods can be given as multiple arguments.
        Normally this should not be needed as sort methods are auto detected.

        :param int methods: One or more kodi sort methods.

        .. seealso:: The full list of sort methods can be found at.\n
                     https://codedocs.xyz/xbmc/xbmc/group__python__xbmcplugin.html#ga85b3bff796fd644fb28f87b136025f40
        """
        self._manual_sort.update(methods)
