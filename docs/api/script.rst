Script
======
This module is used for creating "Script" callback's, which are also used as the base for all other types of callbacks.

.. autofunction:: codequick.run

.. autoclass:: codequick.script.Script
    :members:

    .. attribute:: handle
        :annotation: = -1

        The Kodi handle that this add-on was started with.

.. autoclass:: codequick.script.Settings

    .. automethod:: __getitem__
    .. automethod:: __setitem__
    .. automethod:: get_string(key, addon_id=None)
    .. automethod:: get_boolean(key, addon_id=None)
    .. automethod:: get_int(key, addon_id=None)
    .. automethod:: get_number(key, addon_id=None)
