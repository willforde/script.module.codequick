============
Introduction
============
Codequick is a framework for kodi add-on's. The goal of this framework is to simplify add-on development.
This is achieved by reducing the amount of boilerplate code to a minimum, automating tasks like route dispatching
and sort method selection. Ultimately allowing the developer to focus primarily on scraping content from websites
and passing it to kodi.

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
