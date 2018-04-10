Script
======
This module is used for creating script callbacks witch are also used as the base for all other types of callbacks.

.. autoclass:: codequick.script.Script
    :members:

.. autoclass:: codequick.script.Settings

    .. automethod:: __getitem__
    .. automethod:: __setitem__
    .. automethod:: get_string(key, addon_id=None)
    .. automethod:: get_boolean(key, addon_id=None)
    .. automethod:: get_int(key, addon_id=None)
    .. automethod:: get_number(key, addon_id=None)
