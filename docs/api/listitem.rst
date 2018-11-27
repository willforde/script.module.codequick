Listitem
========
The "listitem" control is used for the creating  of item lists in Kodi.

.. autoclass:: codequick.listing.Listitem
    :members:
    :exclude-members: info, art, stream, context, params, property, subtitles

    .. autoinstanceattribute:: subtitles
        :annotation: = list()

    .. autoinstanceattribute:: art
        :annotation: = Art()

    .. autoinstanceattribute:: info
        :annotation: = Info()

    .. autoinstanceattribute:: stream
        :annotation: = Stream()

    .. autoinstanceattribute:: context
        :annotation: = Context()

    .. autoinstanceattribute:: property
        :annotation: = dict()

    .. autoinstanceattribute:: params
        :annotation: = dict()

.. autoclass:: codequick.listing.Art
    :members:

.. autoclass:: codequick.listing.Info
    :members:

.. autoclass:: codequick.listing.Stream
    :members:

.. autoclass:: codequick.listing.Context
    :members:
