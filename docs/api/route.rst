Route
=====

.. autoclass:: codequick.route.Route
    :members: add_sort_methods

    .. attribute:: autosort
        :annotation: = True

        Set to ``False`` to disable autosort.

    .. attribute:: update_listing
        :annotation: = False

        When set to ``True`` the current lsting will be updated

    .. attribute:: content_type
        :annotation: = None

        The add-on's content type. If not given it will default to files/videos, based on type of content.

        * 'files' when listing folders.
        * 'videos' when listing videos.

        .. seealso:: The full list of content types can be found at.

                     https://codedocs.xyz/xbmc/xbmc/group__python__xbmcplugin.html#gaa30572d1e5d9d589e1cd3bfc1e2318d6