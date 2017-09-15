# -*- coding: utf-8 -*-

# Standard Library Imports
from xml.etree import ElementTree as ETree
from collections import Mapping, OrderedDict
from xml.dom import minidom
from codecs import open
import requests
import logging
import zipfile
import shutil
import time
import sys
import os
import re

# Package Imports
from codequickcli.utils import CacheProperty, ensure_unicode, ensure_native_str, safe_path

# Base logger
logger = logging.getLogger("cli")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter("%(relativeCreated)-13s %(levelname)7s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# Dictionary of available addons
kodi_paths = OrderedDict()
avail_addons = dict()
data_pipe = None
plugin_id = ""

# Data store for addon. Use in xbmcplugin and xbmcgui
plugin_data = {"succeeded": False, "updatelisting": False, "resolved": None, "contenttype": None,  "category": None,
               "sortmethods": [], "playlist": [], "listitem": []}

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


def initializer(plugin_path):
    """
    Setup & initialize the mock kodi environment.

    :param plugin_path: The path to the plugin that will be executed.
    """
    global plugin_id
    system_dir, addon_dir = setup_paths(plugin_path)
    plugin_id = os.path.basename(plugin_path)

    # Ensure that all directories exists
    for path in kodi_paths.values():
        path = safe_path(path)
        if not os.path.exists(path):
            os.mkdir(path)

    # First available addon with be the starting plugin
    avail_addons[plugin_id] = addon = Addon.from_file(os.path.join(plugin_path, u"addon.xml"))
    sys.path.insert(0, plugin_path)
    os.chdir(plugin_path)

    # Preload all existing addons
    for plugin_file in find_addons(system_dir, addon_dir):
        req_addon = Addon.from_file(plugin_file)
        avail_addons[req_addon.id] = req_addon

    # Populate mock environment of required addons
    process_dependencies(addon.requires)
    return addon


def setup_paths(plugin_path):
    # Location of support files
    system_dir = os.path.join(ensure_unicode(os.path.dirname(__file__), sys.getfilesystemencoding()), u"system")
    kodi_paths["support"] = system_dir

    # Kodi path structure
    kodi_paths["home"] = home = os.path.join(plugin_path, u".kodi")
    kodi_paths["addons"] = addon_dir = os.path.join(home, u"addons")
    kodi_paths["packages"] = os.path.join(addon_dir, u"packages")
    kodi_paths["temp"] = temp_dir = os.path.join(home, u"temp")
    kodi_paths["system"] = os.path.join(home, u"system")
    kodi_paths["profile"] = userdata = os.path.join(home, u"userdata")
    kodi_paths["data"] = os.path.join(userdata, u"addon_data")
    kodi_paths["database"] = os.path.join(userdata, u"Database")
    kodi_paths["thumbnails"] = os.path.join(userdata, u"Thumbnails")
    kodi_paths["playlists"] = playlists = os.path.join(userdata, u"playlists")
    kodi_paths["musicplaylists"] = os.path.join(playlists, u"music")
    kodi_paths["videoplaylists"] = os.path.join(playlists, u"video")

    # Ensure that all directories exists
    for path in kodi_paths.values():
        path = safe_path(path)
        if not os.path.exists(path):
            os.mkdir(path)

    # Rest of kodi's special paths
    kodi_paths["logpath"] = os.path.join(temp_dir, u"kodi.log")
    kodi_paths["masterprofile"] = userdata
    kodi_paths["masterprofile"] = userdata
    kodi_paths["userdata"] = userdata
    kodi_paths["subtitles"] = temp_dir
    kodi_paths["recordings"] = temp_dir
    kodi_paths["screenshots"] = temp_dir
    kodi_paths["cdrips"] = temp_dir
    kodi_paths["skin"] = temp_dir
    kodi_paths["xbmc"] = home

    # Return the support system directory and addon directory
    return system_dir, addon_dir


def find_addons(*dirs):
    """
    Search given directory for addons.

    A folder is considered to be an addon, if it contains an 'addon.xml' file.

    :param dirs: A list of directorys to scan.
    """
    filename = safe_path("addon.xml")
    for path in dirs:
        path = safe_path(path)
        for item in os.listdir(path):
            plugin_file = os.path.join(path, item, filename)
            if os.path.exists(plugin_file):
                yield ensure_unicode(plugin_file)


def process_dependencies(deps):
    download = []
    for dep in deps:
        # Check if we already have the dependency
        if dep.id in avail_addons:
            addon = avail_addons[dep.id]
            # Check if the addon is a module
            # Register the module path if so
            addon.register_module()

            # Update the current set of dependencies
            for sub_dep in addon.requires:
                if sub_dep not in deps:
                    deps.append(sub_dep)

            # Check if the current cached addon is outdated
            if dep.version > addon.version and dep not in download:
                download.append(dep)
        else:
            download.append(dep)

    repo = Repo()
    if download:
        repo.fetch(download)


class Dependency(object):
    __slots__ = ["id", "version", "optional"]

    def __init__(self, addonid, version, optional):
        self.id = addonid
        self.version = version
        self.optional = optional

    def __eq__(self, other):
        return other.id == self.id


class Addon(object):
    """
    Add-on Information.

    :ivar str id: The add-on id.
    :ivar str name: The add-on name.
    :ivar str author: The add-on author.
    :ivar str version: The add-on version.
    :ivar str path: The path to the add-on source directory.
    :ivar str profile: The path to the add-on profile data directory.
    """

    def __init__(self, xml_node):
        self._xml = xml_node

        # Extract required data from addon.xml
        self.id = xml_node.attrib["id"]
        self.name = xml_node.get("name", "")
        self.version = xml_node.attrib["version"]
        self.author = xml_node.get("provider-name", "")

        # The metadata of the add-on
        self._metadata = self._xml.find("./extension[@point='xbmc.addon.metadata']")
        self.profile = os.path.join(kodi_paths["data"], self.id)
        self.path = u""

    def register_module(self):
        """Append addon library path to sys.path if addon is a module."""
        data = self._xml.find("./extension[@point='xbmc.python.module']")
        if data is not None:
            library_path = ensure_native_str(os.path.join(self.path, os.path.normpath(data.attrib["library"])))
            if library_path not in sys.path:
                sys.path.insert(0, library_path)

    @CacheProperty
    def strings(self):
        """The add-on strings.po language file."""
        return Strings(self.path)

    @CacheProperty
    def settings(self):
        """The add-on settings file."""
        return Settings(self.path, self.profile)

    @CacheProperty
    def entry_point(self):
        """Return the library entry poin."""
        data = self._xml.find("./extension[@point='xbmc.python.pluginsource']")
        if data is None:
            return None
        else:
            return data.attrib["library"][:-3]

    @CacheProperty
    def provides(self):
        """
        All list content that this addon provides e.g. video, audio.

        :returns: A list of content providers
        :rtype: list
        """
        data = self._xml.find("./extension[@point='xbmc.python.pluginsource']/provides")
        if data:
            return [provider.strip() for provider in data.text.split(" ")]
        else:
            return []

    @property
    def requires(self):
        """
        All list of required plugins needed for this addon to work.

        :returns: A list of Dependency objects consisting of (id, version, optional)
        :rtype: list
        """
        return [Dependency(imp.attrib["addon"], imp.attrib["version"], imp.get("optional", "false") == "true")
                for imp in self._xml.findall("requires/import")]

    @CacheProperty
    def description(self):
        """Addon description."""
        return self._lang_type("description")

    @CacheProperty
    def disclaimer(self):
        """Addon disclaimer."""
        return self._lang_type("disclaimer")

    @CacheProperty
    def summary(self):
        """Addon summary."""
        return self._lang_type("summary")

    def _lang_type(self, name):
        """Extract and return the english language text."""
        node = self._metadata.findall(name)
        for data in node:
            if data.get("lang", "en").lower().startswith("en"):
                return data.text

        if node is None:
            return ""
        else:
            return node[0].text

    @CacheProperty
    def icon(self):
        """Addon icon image path."""
        return self._path_type("./assets/icon", u"icon.png")

    @CacheProperty
    def fanart(self):
        """Addon fanart image path."""
        return self._path_type("./assets/fanart", u"fanart.jpg")

    def _path_type(self, metapath, default):
        """Return the path to required file, e.g. fanart, icon."""
        path = self._metadata.find(metapath)
        if path is None:
            return os.path.join(self.path, default)
        else:
            return os.path.join(self.path, os.path.normpath(path.text))

    def changelog(self):
        data = self._metadata.findall("news")
        if data is not None:
            return data.text
        else:
            changelog_file = safe_path(os.path.join(self.path, u"changelog-{}.txt".format(self.version)))
            if os.path.exists(changelog_file):
                with open(changelog_file, "r", "utf8") as stream:
                    return stream.read()

    @CacheProperty
    def type(self):
        """Addon type."""
        # Search for all extensions that are not metadat and hope that what is left is what we want
        exts = [ext for ext in self._xml.findall("extension") if ext is not self._metadata]
        if exts:
            return exts[0].get("point")
        else:
            return ""

    @CacheProperty
    def stars(self):
        """Return the star rating for this addon."""
        return "-1"

    @classmethod
    def from_file(cls, xml_path):
        xmldata = ETree.parse(safe_path(xml_path)).getroot()
        obj = cls(xmldata)
        obj.path = os.path.dirname(xml_path)
        return obj

    def __eq__(self, other):
        return other == self.id

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return "Addon(id={})".format(self.id)


class Repo(object):
    """Check the official kodi repositories for available addons."""

    # Kodi version code names for repository linking
    repo_url = "http://mirrors.kodi.tv/addons/krypton/{}"

    def __init__(self):
        self._addon_dir = kodi_paths["addons"]
        self._package_dir = kodi_paths["packages"]
        self._session = requests.session()
        self.db = {}

        # Check if an update is scheduled
        self.update_file = safe_path(os.path.join(kodi_paths["temp"], u"update_check"))
        if self.update_required():
            self.update()

    def update_required(self, max_age=432000):
        """Return True if its time to update."""
        if os.path.exists(self.update_file):
            update = (time.time() - os.stat(self.update_file).st_mtime) > max_age
            if update:
                # Reset the timestamp of the check file
                os.utime(self.update_file, None)
            return update
        else:
            # Create missing check file and force update
            open(self.update_file, "w").close()
            return True

    def populate(self):
        """Search for all available addons."""
        logger.info("Communicating with kodi's official repository: Please wait.")
        url = self.repo_url.format("addons.xml")
        raw_xml = requests.get(url).content
        addon_xml = ETree.fromstring(raw_xml)
        for node in addon_xml.iterfind("addon"):
            addonid = node.attrib["id"]
            self.db[addonid] = Addon(node)

    def update(self):
        """Check if any cached plugins need updating."""
        if not self.db:
            self.populate()

        requires = []
        for addon in avail_addons.values():
            # Add addon to requires list if cached addon is outdated
            if addon.id in self.db and addon.version < self.db[addon.id].version:
                requires.append(Dependency(addon.id, self.db[addon.id].version, False))

        if requires:
            self.fetch(requires)

    def fetch(self, required):
        """
        Fetch any required addons.

        :param list required: List of required dependencies."""
        if not self.db:
            self.populate()

        # Process required addons befor downloading
        for req_dep in required:
            if req_dep.id in self.db:
                addon = self.db[req_dep.id]

                # Check that the versin of the available addon is greater or equal to required addon
                if addon.version >= req_dep.version:
                    # Check dependency of required addon
                    for dep in addon.requires:
                        if dep not in required and dep.id not in avail_addons:
                            required.append(dep)

                    # Now we download the addon
                    self.download(addon)
                else:
                    raise ValueError("required version is greater than whats available: need {} - have {}"
                                     .format(req_dep.version, addon.version))

            # Raise error only if addon is not actually required(optional)
            elif req_dep.optional is False:
                raise KeyError("unable to find required dependency: '{}'".format(req_dep.id))

    def download(self, addon):
        """
        Download any requred addon

        :param Addon addon: The addon to download
        """
        filename = u"{0}-{1}.zip".format(addon.id, addon.version)
        tmp = safe_path(os.path.join(self._package_dir, filename))
        logger.info("Downloading: '{}'".format(filename.encode("utf8")))

        # Remove old zipfile before download
        # This will prevent an error if the addon was manually removed by user
        if os.path.exists(tmp):
            os.remove(tmp)

        # Request the addon zipfile from server
        url_part = "{0}/{1}".format(addon.id, filename)
        url = self.repo_url.format(url_part)
        resp = self._session.get(url)

        # Read and save contents of zipfile to package directory
        with open(tmp, "wb") as stream:
            for chunk in resp.iter_content(decode_unicode=False):
                stream.write(chunk)

        # Remove the old plugin directory if exists
        # This is needed when updating addons
        udst = os.path.join(self._addon_dir, addon.id)
        sdst = safe_path(udst)
        if os.path.exists(sdst):
            shutil.rmtree(sdst)

        resp.close()
        self.extract_zip(tmp)

        addon.path = udst
        addon.register_module()
        avail_addons[addon.id] = addon

    def extract_zip(self, src):
        """Extract all content of zipfile to addon directoy."""
        zipobj = zipfile.ZipFile(src)
        zipobj.extractall(self._addon_dir)


class Strings(Mapping):
    def __init__(self, plugin_path):
        self._strings = {}

        # Locate and extract stirngs data
        self._search_strings(os.path.join(plugin_path, "resources"))

    def _search_strings(self, resources_path):
        # Possible locations for english strings.po
        string_loc = [os.path.join(resources_path, "strings.po"),
                      os.path.join(resources_path, "language", "English", "strings.po"),
                      os.path.join(resources_path, "language", "resource.language.en_gb", "strings.po"),
                      os.path.join(resources_path, "language", "resource.language.en_us", "strings.po")]

        # Return the first strings.po file that is found
        for path in string_loc:
            path = safe_path(path)
            if os.path.exists(path):
                return self._extractor(path)

        # Unable to find a strings.po file
        # Search for any strings.po file
        strtext = safe_path("strings.po")
        for root, _, files in os.walk(safe_path(os.path.join(resources_path, "language"))):
            if strtext in files:
                return self._extractor(os.path.join(root, strtext))

    def _extractor(self, strings_path):
        """Extract the strings from the strings.po file"""
        with open(strings_path, "r", "utf-8") as stream:
            file_data = stream.read()

        # Populate dict of strings
        search_pattern = 'msgctxt\s+"#(\d+)"\s+msgid\s+"(.+?)"\s+msgstr\s+"(.*?)'
        for strID, msgID, msStr in re.findall(search_pattern, file_data):
            self._strings[int(strID)] = msStr if msStr else msgID

    def __getitem__(self, key):
        return ensure_unicode(self._strings.get(key, u""))

    def __iter__(self):
        return iter(self._strings)

    def __len__(self):
        return len(self._strings)


class Settings(dict):
    def __init__(self, plugin_path, plugin_profile):
        super(Settings, self).__init__()

        # Populate settings from the addon source settings file
        settings_path = safe_path(os.path.join(plugin_path, "resources", "settings.xml"))
        if os.path.exists(settings_path):
            xmldata = ETree.parse(settings_path).getroot()
            self._extractor(xmldata)

        # Populate settings from the addon saved profile settings file
        self._settings_path = settings_path = safe_path(os.path.join(plugin_profile, "settings.xml"))
        if os.path.exists(settings_path):
            xmldata = ETree.parse(settings_path).getroot()
            self._extractor(xmldata)

    def _extractor(self, xmldata):
        """Extract the strings from the strings.po file"""
        for setting in xmldata.findall(".//setting"):
            setting_id = setting.get("id")
            if setting_id:
                super(Settings, self).__setitem__(setting_id, setting.get("value", setting.get("default", "")))

    def __getitem__(self, item):
        return ensure_unicode(self.get(item, u""))

    def __setitem__(self, key, value):
        """Set an add-on setting."""
        if not isinstance(value, (bytes, unicode)):
            raise TypeError("argument 'value' for method 'setSetting' must be unicode or str not '%s'" % type(value))

        # Save setting to local dict before saving to disk
        super(Settings, self).__setitem__(key, value)

        # The easyest way to store the setting is to store all setting
        tree = ETree.Element("settings")
        for key, value in self.items():
            ETree.SubElement(tree, "setting", {"id": key, "value": value})

        # Create plugin data directory if don't exist
        settings_dir = os.path.dirname(self._settings_path)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        raw_xml = minidom.parseString(ETree.tostring(tree)).toprettyxml(indent=" "*4, encoding="utf8")
        with open(self._settings_path, "wb") as stream:
            stream.write(raw_xml)


def handle_prompt(prompt):
    if data_pipe:
        data_pipe.send({"prompt": prompt})
        return data_pipe.recv()
    else:
        return input(prompt)
