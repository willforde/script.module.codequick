"""
Offers classes and functions that manipulate the add-on settings, information and localization.
"""

# Standard Library Imports
import os

# Package imports
from codequickcli import addondb
from codequickcli.support import ensure_unicode, unicode_type

__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:07 BST 2015'
__platform__ = 'ALL'
__version__ = '2.25.0'


# noinspection PyShadowingBuiltins
class Addon(object):
    """
    Addon(id=None)

    Creates a new Addon class.

    :param id: [opt] string - id of the addon as specified in addon.xml

    .. note: Specifying the addon id is not needed.
             Important however is that the addon folder has the same name as the AddOn id provided in addon.xml.
             You can optionally specify the addon id from another installed addon to retrieve settings from it.

    Example::

        self.Addon = xbmcaddon.Addon()
        self.Addon = xbmcaddon.Addon('script.foo.bar')
    """

    def __init__(self, id=None):
        if id is None:
            id = os.path.basename(os.getcwd())
            if not (id.startswith("plugin.") or id.startswith("script.")):
                id = "script.module.codequick"
        self._data = addondb.db[id]

    def getAddonInfo(self, id):
        """
        Returns the value of an addon property as a string.

        :type id: str
        :param id: string - id of the property that the module needs to access.
        :returns: AddOn property as a string.
        :rtype: str

        Choices are::

            author, changelog, description, disclaimer, fanart, icon,
            id, name, path, profile, stars, summary, type, version

        Example::

            version = self.Addon.getAddonInfo('version')
        """
        return getattr(self._data, id, "")

    def getLocalizedString(self, id):
        """
        Returns an addon's localize 'unicode string'.

        :param int id: integer - id# for string you want to localize.
        :returns: Localized 'unicode string'
        :rtype: unicode

        Example::

            locstr = self.Addon.getLocalizedString(32000)
        """
        return ensure_unicode(self._data.strings[id])

    def getSetting(self, id):
        """
        Returns the value of a setting as a unicode string.

        :param str id: string - id of the setting that the module needs to access.
        :returns: Setting as a unicode string
        :rtype: unicode

        Example::

            apikey = self.Addon.getSetting('apikey')
        """
        return ensure_unicode(self._data.settings[id])

    def getSettingBool(self, id):
        """
        Returns the value of a setting as a boolean.

        :param str id: string - id of the setting that the module needs to access.
        :returns: Setting as a boolean
        :rtype: bool

        Example::

            enabled = self.Addon.getSettingBool('enabled')
        """
        setting = self.getSetting(id)
        return setting == u"true" or setting == u"1"

    def getSettingInt(self, id):
        """
        Returns the value of a setting as an integer.

        :param str id: string - id of the setting that the module needs to access.
        :returns: Setting as an integer
        :rtype: int

        Example::

            max = self.Addon.getSettingInt('max')
        """
        return int(self.getSetting(id))

    def getSettingNumber(self, id):
        """
        Returns the value of a setting as a floating point number.

        :param str id: string - id of the setting that the module needs to access.
        :returns: Setting as a floating point number
        :rtype: float

        Example::

            max = self.Addon.getSettingNumber('max')
        """
        return float(self.getSetting(id))

    def getSettingString(self, id):
        """
        Returns the value of a setting as a unicode string.

        :param str id: string - id of the setting that the module needs to access.
        :returns: Setting as a unicode string
        :rtype: unicode

        Example::

            apikey = self.Addon.get_setting('apikey')
        """
        return self.getSetting(id)

    # noinspection PyMethodMayBeStatic
    def openSettings(self):
        """Opens this addon settings dialog."""
        pass

    def setSetting(self, id, value):
        """
        Sets a script setting.

        :param str id: string - id of the setting that the module needs to access.
        :param value: string or unicode - value of the setting.
        :type value: str or unicode

        .. note:: You can use the above as keywords for arguments.

        Example::

            self.Addon.setSetting(id='username', value='teamkodi')
        """
        self._data.settings[id] = ensure_unicode(value)

    def setSettingBool(self, id, value):
        """
        Sets a script setting.

        :param str id: string - id of the setting that the module needs to access.
        :param bool value: boolean - value of the setting.

        :returns: True if the value of the setting was set, false otherwise
        :rtype: bool

        .. note:: You can use the above as keywords for arguments.

        Example::

            self.Addon.setSettingBool(id='enabled', value=True)
        """
        if isinstance(value, bool):
            self.setSetting(id, str(value).lower())
            return True
        else:
            return False

    def setSettingInt(self, id, value):
        """
        Sets a script setting.

        :param str id: string - id of the setting that the module needs to access.
        :param int value: integer - value of the setting.

        :returns: True if the value of the setting was set, false otherwise
        :rtype: bool

        .. note:: You can use the above as keywords for arguments.

        Example::

            self.Addon.setSettingInt(id='max', value=5)
        """
        if isinstance(value, int):
            self.setSetting(id, str(value))
            return True
        else:
            return False

    def setSettingNumber(self, id, value):
        """
        Sets a script setting.

        :param str id: string - id of the setting that the module needs to access.
        :param value: float - value of the setting.
        :type value: float

        :returns: True if the value of the setting was set, false otherwise
        :rtype: bool

        .. note:: You can use the above as keywords for arguments.

        Example::

            self.Addon.setSettingNumber(id='max', value=5.5)
        """
        if isinstance(value, float):
            self.setSetting(id, str(value))
            return True
        else:
            return False

    def setSettingString(self, id, value):
        """
        Sets a script setting.

        :param str id: string - id of the setting that the module needs to access.
        :param value: string or unicode - value of the setting.
        :type value: str or unicode

        :returns: True if the value of the setting was set, false otherwise
        :rtype: bool

        .. note:: You can use the above as keywords for arguments.

        Example::

            self.Addon.setSettingString(id='username', value='teamkodi')
        """
        if isinstance(value, (str, unicode_type)):
            self.setSetting(id, value)
            return True
        else:
            return False
