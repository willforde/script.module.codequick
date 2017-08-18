# Standard Library Imports
from xml.etree import ElementTree as ETree
import unicodedata
import hashlib
import codecs
import sys
import os
import re

# Kodi user directory
KODI_INSTALL_PATH = os.path.realpath("/usr/share/kodi")
KODI_SOURCE_PATH = os.path.join(KODI_INSTALL_PATH, "addons")
KODI_PROFILE_PATH = os.path.realpath("/home/willforde/.kodi")
KODI_ADDON_PATH = os.path.join(KODI_PROFILE_PATH, "addons")
KODI_TEMP_PATH = os.path.join(KODI_PROFILE_PATH, "temp")
KODI_DATA_PATH = os.path.join(KODI_PROFILE_PATH, "userdata", "addon_data")

# Kodi paths mapping. Used by xbmc.translatePath
path_map = {"home": KODI_PROFILE_PATH,
            "temp": KODI_TEMP_PATH,
            "profile": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "masterprofile": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "userdata": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "subtitles": KODI_TEMP_PATH,
            "database": os.path.join(KODI_PROFILE_PATH, "userdata", "Database"),
            "thumbnails": os.path.join(KODI_PROFILE_PATH, "userdata", "Thumbnails"),
            "musicplaylists": os.path.join(KODI_PROFILE_PATH, "userdata", "playlists", "music"),
            "videoplaylists": os.path.join(KODI_PROFILE_PATH, "userdata", "playlists", "video"),
            "recordings": KODI_TEMP_PATH,
            "screenshots": KODI_TEMP_PATH,
            "cdrips": KODI_TEMP_PATH,
            "xbmc": KODI_INSTALL_PATH,
            "logpath": os.path.join(KODI_TEMP_PATH, "kodi.log"),
            "skin": KODI_TEMP_PATH}

# Region settings. Used by xbmc.getRegion
region_settings = {"datelong": "%A, %d %B %Y", "dateshort": "%d/%m/%Y",
                   "time": "%H:%M:%S", "meridiem": "PM", "speedunit": "km/h"}

# Dict of supported media types that kodi is able to play. Used by xbmc.getSupportedMedia
supported_media = {"video": ".m4v|.3g2|.3gp|.nsv|.tp|.ts|.ty|.strm|.pls|.rm|.rmvb|.mpd|.m3u|.m3u8|.ifo|.mov|.qt|.divx"
                            "|.xvid|.bivx|.vob|.nrg|.img|.iso|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg"
                            "|.mp4|.mkv|.mk3d|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.rar|.001|.wpl|.zip|.vdr|.dvr"
                            "-ms|.xsp|.mts|.m2t|.m2ts|.evo|.ogv|.sdp|.avs|.rec|.url|.pxml|.vc1|.h264|.rcv|.rss|.mpls"
                            "|.webm|.bdmv|.wtv|.pvr|.disc",
                   "music": ".nsv|.m4a|.flac|.aac|.strm|.pls|.rm|.rma|.mpa|.wav|.wma|.ogg|.mp3|.mp2|.m3u|.gdm|.imf"
                            "|.m15|.sfx|.uni|.ac3|.dts|.cue|.aif|.aiff|.wpl|.ape|.mac|.mpc|.mp+|.mpp|.shn|.zip|.rar"
                            "|.wv|.dsp|.xsp|.xwav|.waa|.wvs|.wam|.gcm|.idsp|.mpdsp|.mss|.spt|.rsd|.sap|.cmc|.cmr|.dmc"
                            "|.mpt|.mpd|.rmt|.tmc|.tm8|.tm2|.oga|.url|.pxml|.tta|.rss|.wtv|.mka|.tak|.opus|.dff|.dsf"
                            "|.cdda",
                   "picture": ".png|.jpg|.jpeg|.bmp|.gif|.ico|.tif|.tiff|.tga|.pcx|.cbz|.zip|.cbr|.rar|.rss|.webp"
                              "|.jp2|.apng"}

# Data store for addon. Use in xbmcplugin and xbmcgui
plugin_data = {"succeeded": False, "updatelisting": False, "resolved": None, "contenttype": None,  "category": None,
               "sortmethods": [], "playlist": [], "listitem": []}

# Data pipe when running as a supprocess
data_pipe = None


# Used by xbmc.makeLegalFilename
def normalize_filename(filename):
    """
    Returns a legal filename or path as a string.

    :param filename:
    :type filename: str or unicode

    :return: Legal filename or path as a string
    :rtype: str
    """
    value = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


# Used by xbmcgui.Dialog.input
def hash_password(password):
    """
    Hash a giving password using md5 and return the hash value.

    :param str password: The password to hash
    :returns: The password as a md5 hash
    :rtype: str
    """
    return hashlib.md5(password).hexdigest()


def handle_prompt(prompt):
    if data_pipe:
        data_pipe.send({"prompt": prompt})
        return data_pipe.recv()
    else:
        return raw_input(prompt)


def addon_search(pluginid):
    """
    Search kodi data paths for given plugin.

    :param pluginid: The id of the plugin.
    :type pluginid: str

    :return: The location of plugin.
    :rtype: str

    :raises RuntimeError: If unable to find plugin.
    """
    # Check that plugin id exists
    addon_path = os.path.join(KODI_ADDON_PATH, pluginid)
    if not os.path.exists(addon_path):
        addon_path = os.path.join(KODI_SOURCE_PATH, pluginid)
        if not os.path.exists(addon_path):
            raise RuntimeError("failed to find specified plugin id in addon db: %s", pluginid)

    # Return the path to found addon
    return addon_path

class Strings(dict):
    def __init__(self, addon_path):
        super(Strings, self).__init__()
        # Location of the stirngs.po file
        strings_path = os.path.join(addon_path, "resources", "language", "English", "strings.po")
        if not os.path.exists(strings_path):
            strings_path = os.path.join(addon_path, "resources", "strings.po")
            if not os.path.exists(strings_path):
                return

        # Extract data from strings.po
        self._extractor(strings_path)

    def _extractor(self, strings_path):
        """Extract the strings from the strings.po file"""
        with codecs.open(strings_path, "r", "utf-8") as stream:
            file_data = stream.read()

        # Populate dict of strings
        search_pattern = 'msgctxt\s+"#(\d+)"\s+msgid\s+"(.+?)"\s+msgstr\s+"(.*?)'
        for strID, msgID, msStr in re.findall(search_pattern, file_data):
            super(Strings, self).__setitem__(int(strID), msStr if msStr else msgID)

    def __missing__(self, key):
        """Return empty string to emulate what kodi would do."""
        return ""

    def __setitem__(self, key, value):
        raise NotImplementedError("this method is not allowed for '%s'" % type(self))


class Settings(dict):
    def __init__(self, addon_path, addon_profile):
        super(Settings, self).__init__()
        self._xml = None

        # Populate settings from the addon source settings file
        settings_path = os.path.join(addon_path, "resources", "settings.xml")
        if os.path.exists(settings_path):
            xmldata = ETree.parse(settings_path).getroot()
            self._extractor(xmldata)

        # Populate settings from the addon saved profile settings file
        self._settings_path = settings_path = os.path.join(addon_profile, "settings.xml")
        if os.path.exists(settings_path):
            self._xml = xmldata = ETree.parse(settings_path).getroot()
            self._extractor(xmldata)

    def _extractor(self, xmldata):
        """Extract the strings from the strings.po file"""
        for setting in xmldata.findall("setting"):
            setting_id = setting.get("id")
            if setting_id:
                super(Settings, self).__setitem__(setting_id, setting.get("value", setting.get("default", "")))

    def __missing__(self, key):
        """Return empty string to emulate what kodi would do."""
        return ""

    def __setitem__(self, key, value):
        """Set an add-on setting."""
        if not isinstance(value, (str, unicode)):
            raise TypeError("argument 'value' for method 'setSetting' must be unicode or str")

        # Save setting to local dict before saving to disk
        super(Settings, self).__setitem__(key, value)

        # Change state of xml file if xml file is loaded
        if self._xml is not None:
            setting = self._xml.find("setting[@id='%s']" % key)
            setting.set(key, value)
        else:
            # Create xml file
            self._xml = tree = ETree.Element("settings")
            for key, value in self.iteritems():
                ETree.SubElement(tree, "setting", {"id": key, "value": value})

        settings_dir = os.path.dirname(self._settings_path)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        with open(self._settings_path, "wb") as stream:
            stream.write(ETree.tostring(self._xml))


class Addon(object):
    """
    Access the add-on settings, information and localization.

    :ivar str id: The id of the add-on.
    :ivar str name: The name of the add-on.
    :ivar str author: The author of the add-on.
    :ivar str version: The version of the add-on.
    :ivar str path: The path to the add-on source directory.
    :ivar str profile: The path to the add-on profile data directory.
    :ivar dict settings: A dictionary of add-on settings.
    :ivar dict strings: A dictionary of localized string ids.
    """
    def __init__(self, pluginid):
        self.path = addon_path = addon_search(pluginid)
        self.profile = profile = os.path.join(KODI_DATA_PATH, pluginid)

        # Parse the addon.xml file
        addon_xml_path = os.path.join(addon_path, "addon.xml")
        self._xml = addon_xml = ETree.parse(addon_xml_path).getroot()

        # Extract required data from addon.xml
        self.id = pluginid
        self.name = addon_xml.get("name", pluginid.split(".")[-1].title())
        self.author = addon_xml.attrib["provider-name"]
        self.version = addon_xml.attrib["version"]

        # Append addon library path to sys.path if addon is a module
        data = addon_xml.find("./extension[@point='xbmc.python.module']")
        if data is not None:
            library_path = os.path.join(addon_path, data.attrib["library"])
            sys.path.insert(0, library_path)

        # The metadata of the add-on
        self._metadata = self._xml.find("./extension[@point='xbmc.addon.metadata']")

        # The add-on strings.po language file
        self.strings = Strings(addon_path)

        # The add-on settings file
        self.settings = Settings(addon_path, profile)

    @property
    def requires(self):
        """All required plugins needed for this addon to work."""
        for imp in self._xml.findall("requires/import"):
            yield imp.attrib["addon"], imp.attrib["version"], imp.get("optional", "false") == "true"

    @property
    def icon(self):
        """Addon icon image path."""
        # Extract icon from addon assets or default to default icon location
        icon = self._metadata.find("./assets/icon")
        if icon is None:
            return os.path.join(self.path, "icon.png")
        else:
            return os.path.join(self.path, os.path.normpath(icon.text))

    @property
    def fanart(self):
        """Addon fanart image path."""
        # Extract icon from addon assets or default to default icon location
        fanart = self._metadata.find("./assets/fanart")
        if fanart is None:
            return os.path.join(self.path, "fanart.jpg")
        else:
            return os.path.join(self.path, os.path.normpath(fanart.text))

    @property
    def description(self):
        """Addon description."""
        for data in self._metadata.findall("description"):
            if data.get("lang", "en") == "en":
                return data
        else:
            return ""

    @property
    def disclaimer(self):
        """Addon disclaimer."""
        for data in self._metadata.findall("disclaimer"):
            if data.get("lang", "en") == "en":
                return data
        else:
            return ""

    @property
    def summary(self):
        """Addon summary."""
        for data in self._metadata.findall("summary"):
            if data.get("lang", "en") == "en":
                return data
        else:
            return ""

    @property
    def type(self):
        """Addon type."""
        data = self._xml.find("./extension[@point='xbmc.python.pluginsource']/provides")
        if data is None:
            return ""
        else:
            return data.text

    @property
    def changelog(self):
        return os.path.join(self.path, "changelog.txt")

    @property
    def stars(self):
        return "-1"

    @property
    def entry_point(self):
        data = self._xml.find("./extension[@point='xbmc.python.pluginsource']")
        if data is None:
            return None
        else:
            return data.attrib["library"][:-3]


class AddonDB(dict):
    def __init__(self):
        super(AddonDB, self).__init__()

        # Process kodi language file now so not to obscure the timeing results later
        self["resource.language.en_gb"] = self._process("resource.language.en_gb")

    def __getitem__(self, item):
        """:rtype: :class:`Addon`"""
        return super(AddonDB, self).__getitem__(item)

    def __missing__(self, pluginid):
        """Search for missing addon data."""
        self[pluginid] = data = self._process(pluginid)
        return data

    def _process(self, pluginid):
        """Search for plugin and process the addon.xml data."""
        addon = Addon(pluginid)

        # Process all required plugins needed for this addon to work
        for importid, _, optional in addon.requires:
            if importid not in self:
                try:
                    # Process required addon
                    self[importid] = self._process(importid)
                except RuntimeError:
                    # Ignore missing addons if required addon is optional
                    if optional:
                        pass
                    else:
                        raise

        # Return the addon object
        return addon
