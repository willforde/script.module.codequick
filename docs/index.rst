=========
Codequick
=========
Codequick is a framework for kodi add-on's. The goal for this framework is to simplify add-on development.
This is achieved by reducing the amount of boilerplate code to a minimum while automating as many tasks that can be
automated. Ultimately allowing the developer to focus primarily on scraping content from websites and passing it to kodi.

    * Route dispatching (callbacks)
    * Callback arguments can be any python object that can be pickled
    * Delayed execution (execute code after callbacks have returned results)
    * No need to set 'isplayable/isfolder' properties
    * Supports both python2 and python3
    * Auto sort method selection
    * Better error reporting
    * Full unicode support
    * Sets mediatype to 'video/music' depending on listitem type if not set
    * Sets xbmcplugin.setContent base off mediatype infolabel.
    * Sets xbmcplugin.setPluginCategory to the title of current folder
    * Sets thumbnail to add-on icon image if not set
    * Sets fanart to add-on fanart image if not set
    * Sets icon to 'DefaultFolder.png/DefaultVideo.png' if not set
    * Sets Plot to the listitem title if not set
    * Auto type convertion for (str, unicode, int, float, long) infolables and stream info
    * Support for media flags e.g. High definition '720p', audio channels '2.0'
    * Reimplementation of listitem class that makes heavy use of dictionaries
    * Builtin support for saved searches
    * Youtube.dl intergration (https://forum.kodi.tv/showthread.php?tid=200877)
    * Youtube intergration


Contents
========

.. toctree::
    :maxdepth: 2
    :titlesonly:

    tutorial
    api/index
    examples
