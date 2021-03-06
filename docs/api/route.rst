Route
=====
This module is used for the creation of “Route callbacks”.

.. autoclass:: codequick.route.Route
    :members: add_sort_methods

    .. attribute:: autosort
        :annotation: = True

        Set to ``False`` to disable auto sortmethod selection.

        .. note::  If autosort is disabled and no sortmethods are given, then SORT_METHOD_UNSORTED will be set.

    .. attribute:: category

        Manualy specifiy the category for the current folder view.
        Equivalent to setting ``xbmcplugin.setPluginCategory()``

    .. attribute:: redirect_single_item
        :annotation: = False

        When this attribute is set to ``True`` and there is only one folder listitem available in the folder view,
        then that listitem will be automaticly called for you.

    .. attribute:: update_listing
        :annotation: = False

        When set to ``True``, the current page of listitems will be updated, instead of creating a new page of listitems.

    .. attribute:: content_type
        :annotation: = None

        The add-on’s "content type".

        If not given, then the "content type" is based on the "mediatype" infolabel of the listitems.
        If the “mediatype” infolabel” was not set, then it defaults to “files/videos”, based on type of content.

        * "files" when listing folders.
        * "videos" when listing videos.

        .. seealso:: The full list of "content types" can be found at:

                     https://codedocs.xyz/xbmc/xbmc/group__python__xbmcplugin.html#gaa30572d1e5d9d589e1cd3bfc1e2318d6