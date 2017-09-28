########
Tutorial
########
Here we will document the creation of an add-on.
In this case, plugin.video.metalvideo. This will be a simplifyed version of the full add-on
witch can be found @ https://github.com/willforde/plugin.video.metalvideo

First thing is to import the required codequick components.

    * ``Route`` will be used to list folder items.
    * ``Resolver`` will be used to resolve video urls.
    * ``Listitem`` is used to create items within kodi.
    * ``run`` is the function that controls the execution of the add-on.

.. code-block:: python

    from codequick import Route, Resolver, Listitem, run


Next we will create the root function that will be the starting point for the add-on.
It is very important that the root function is called 'root'.

The root function will have to be registered so codequick can find it.
