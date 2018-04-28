Storage
=======
Persistent data storage objects. These objects will act like normal
built-in data types, except all data will be saved to disk for later access when flushed.

.. autoclass:: codequick.storage.PersistentDict
    :members:

    .. automethod:: codequick.storage.PersistentDict.flush
    .. automethod:: codequick.storage.PersistentDict.close


.. autoclass:: codequick.storage.PersistentList
    :members:

    .. automethod:: codequick.storage.PersistentList.flush
    .. automethod:: codequick.storage.PersistentList.close
