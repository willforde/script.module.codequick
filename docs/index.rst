============
Introduction
============
Codequick is a framework for kodi add-on's. The goal of this framework is to simplify add-on development.
This is achieved by reducing the amount of boilerplate code to a minimum, automating as many tasks that can be
automated, like route dispatching and sort method selection. Ultimately allowing the developer to focus primarily
on scraping content from websites and passing it to kodi.

Miscellaneous info.
    * Auto route dispatching (callbacks)
    * Callback arguments can be any python object that can be pickled
    * Auto sort method selection
    * Full unicode support
    * Delayed execution (execute code after content is listed)
    * No need to set 'isplayable/isfolder' properties
    * Better error reporting
    * Intergration with urlquick
    * Youtube.dl intergration
    * Auto set xbmcplugin.setContent base of set mediatype.
    * Sets xbmcplugin.setPluginCategory to the title of previous folder
    * Auto type convertion for (str, unicode, int, float, long) infolables and stream info
    * Sets thumbnail to add-on icon image if not already set
    * Sets fanart to add-on fanart image if not already set
    * Sets icon to 'DefaultFolder.png/DefaultVideo.png' if not already set
    * Sets mediatype to 'video' or 'music' depending on infolable type, if not already set
    * Plot will be set to the title if plot was not manually set
    * Written to support both python2 and python3

This framework utilizes 3 other kodi modules.

    * urlquick: https://github.com/willforde/urlquick
    * htmlement: https://github.com/willforde/python-htmlement
    * youtube.dl: https://forum.kodi.tv/showthread.php?tid=200877

Urlquick is a light-weight http client with requests like interface.
Featuring persistent connections and caching support.

Htmlement is a pure-python HTML parser which aims to be faster than beautifulsoup.
And like beautifulsoup, it will also parse invalid html.
Parsing is then achieved by utilizing ElementTree with XPath expressions.

Youtube-dl is a video downloader written in python and released in the public domain.
It supports 270+ sites and is updated frequently. Can be used to parse video sources and forward them to kodi.


Contents
========

.. toctree::
    :maxdepth: 2
    :titlesonly:

    tutorial
    api/index
    examples
