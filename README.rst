.. image:: https://readthedocs.org/projects/scriptmodulecodequick/badge/?version=stable
    :target: http://scriptmodulecodequick.readthedocs.io/en/stable/?badge=stable

.. image:: https://travis-ci.org/willforde/script.module.codequick.svg?branch=master
    :target: https://travis-ci.org/willforde/script.module.codequick

.. image:: https://coveralls.io/repos/github/willforde/script.module.codequick/badge.svg?branch=master
    :target: https://coveralls.io/github/willforde/script.module.codequick?branch=master

.. image:: https://api.codeclimate.com/v1/badges/dd5a5656d0136127d74b/maintainability
   :target: https://codeclimate.com/github/willforde/script.module.codequick/maintainability
   :alt: Maintainability


=========
Codequick
=========
Codequick is a framework for kodi add-on's. The goal for this framework is to simplify add-on development.
This is achieved by reducing the amount of boilerplate code to a minimum, while automating as many tasks
that can be automated. Ultimately, allowing the developer to focus primarily on scraping content from
websites and passing it to Kodi.

    * Route dispatching (callbacks)
    * Callback arguments can be any Python object that can be "pickled"
    * Delayed execution (execute code after callbacks have returned results)
    * No need to set "isplayable" or "isfolder" properties
    * Supports both Python 2 and 3
    * Auto sort method selection
    * Better error reporting
    * Full unicode support
    * Sets "mediatype" to "video" or "music" depending on listitem type if not set
    * Sets "xbmcplugin.setContent" base off mediatype infolabel.
    * Sets "xbmcplugin.setPluginCategory" to the title of current folder
    * Sets "thumbnail" to add-on icon image if not set
    * Sets "fanart" to add-on fanart image if not set
    * Sets "icon" to "DefaultFolder.png" or "DefaultVideo.png’ if not set
    * Sets "plot" to the listitem title if not set
    * Auto type convertion for (str, unicode, int, float, long) infolables and stream info
    * Support for media flags e.g. High definition '720p', audio channels '2.0'
    * Reimplementation of the listitem class, that makes heavy use of dictionaries
    * Built-in support for saved searches
    * Youtube.DL intergration (https://forum.kodi.tv/showthread.php?tid=200877)
    * URLQuick intergration (http://urlquick.readthedocs.io/en/stable/)
    * Youtube intergration
    * Supports use of "reuselanguageinvoker"


Documentation
-------------
Documentation can be found over at ReadTheDocs.
https://scriptmodulecodequick.readthedocs.io/en/stable/
