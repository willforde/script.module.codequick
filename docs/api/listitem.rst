Listitem
========
The list item control is used for creating item lists in Kodi.

.. autoclass:: codequick.listing.Listitem

    .. attribute:: params

        :class:`Params<codequick.listing.Params>` dictionary object for adding callback parameters.

    .. attribute:: info

        :class:`Info<codequick.listing.Info>` dictionary object for adding infoLabels.

    .. attribute:: art

        :class:`Art<codequick.listing.Art>` dictionary object for adding listitem art.

    .. attribute:: stream

        :class:`Stream<codequick.listing.Stream>` dictionary object for adding stream details.

    .. attribute:: property

        :class:`Property<codequick.listing.Property>` dictionary object for adding listitem properties.

    .. attribute:: context

        :class:`Context<codequick.listing.Context>` dictionary object for context menu items.

    .. attribute:: listitem

        The underlining kodi listitem object, for advanced use.

    .. autoattribute:: codequick.listing.Listitem.label
    .. automethod:: codequick.listing.Listitem.set_callback
    .. automethod:: codequick.listing.Listitem.from_dict
    .. automethod:: codequick.listing.Listitem.next_page
    .. automethod:: codequick.listing.Listitem.youtube
    .. automethod:: codequick.listing.Listitem.recent
    .. automethod:: codequick.listing.Listitem.search


.. autoclass:: codequick.listing.Params
    :members:
    :special-members: __getitem__, __setitem__

.. autoclass:: codequick.listing.Art
    :members:
    :special-members: __getitem__, __setitem__

.. autoclass:: codequick.listing.Info
    :members:
    :special-members: __getitem__, __setitem__

.. autoclass:: codequick.listing.Property
    :members:
    :special-members: __getitem__, __setitem__

.. autoclass:: codequick.listing.Stream
    :members:
    :special-members: __getitem__, __setitem__

.. autoclass:: codequick.listing.Context
    :members:
