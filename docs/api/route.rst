Route
=====
This module is used to create Route callbacks. Route callbacks, are callbacks that
return listitems witch show up as folders in kodi.

.. autoclass:: codequick.route.Route
    :members: add_sort_methods

    .. attribute:: autosort
        :annotation: = True

        Set to ``False`` to disable auto sortmethod selection.

    .. attribute:: update_listing
        :annotation: = False

        When set to ``True``, the current page of listitems will be updated instead of creating a new page of listitems.

    .. attribute:: content_type
        :annotation: = None

        The add-on's content type.

        If not given then the content type is based on the mediatype infolabel of the listitems.
        If the mediatype infolabel was not set then it defaults to files/videos, based on type of content.

        * 'files' when listing folders.
        * 'videos' when listing videos.

        .. seealso:: The full list of content types can be found at.

                     https://codedocs.xyz/xbmc/xbmc/group__python__xbmcplugin.html#gaa30572d1e5d9d589e1cd3bfc1e2318d6